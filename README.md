# Introduction

This is an introduction on how to setup a small development environment with NSO and ansible, including a couple of simulated devices and exercise the available NSO modules:
- `nso_action` - to run actions in NSO
- `nso_config` - to manage configuration through NSO
- `nso_query` - to query the NSO data store
- `nso_show` - to show subtree data from NSO data store
- `nso_verify` - to verify configuration and operational data in NSO

> Please note that the modules we are using in this demo was published with Ansible 2.5, so make sure you are using that version or later.

# Preparing and setting up NSO

You need to have both the NSO and ansible environments setup, meaning you need `$NSO_DIR` to point to an NSO installation and have `ansible-playbook(1)` in your `$PATH`.

NSO is available for free for lab and trials [on DevNet](https://developer.cisco.com/docs/nso/#!getting-nso).

You will need two working directories. One for the NSO runtime files, and one for executing the playbook content. The playbooks that we refer to below are all located in the `devices-playbooks` directory. So make sure you are in that directory when you run them.

Use the `ncs-netsim(1)` tool to prepare to simulate a network consisting of three instances of simulated junos, and cisco IOS-XE.

```
ncs-netsim create-network juniper-junos 3 jnpr
ncs-netsim add-to-network cisco-ios 3 xe
ncs-netsim start
```

This creates all the required files for starting the simulated instances and starts the devices. You can now log into the CLIs of the simulated device using the various `cli*` options to `ncs-netsim(1)`. Take a look at the manpage for more details.

```
ncs-netsim cli-c xe0
ncs-netsim cli jnpr0
```

Next step is to set up the local NSO runtime environment and start it.

```
ncs-setup --dest .
ncs -v --foreground
```

Note that the `ncs-setup` command will pick up on the fact that it is being executed in an environment with netsim set up. It will pick up on the devices added to the netsim network and provide initial configuration in NSO to communicate with them.

The steps above can also be done using the `netsim` and `nso` targets in the local `Makefile`:

```
make netsim nso
```

Start the NSO CLI in a separate terminal and take a look in the configuration subtree (the CLI path is `configuration devices device`) that represents the configuration of the devices under management.

```
ncs_cli -u admin
admin@ncs> show configuration devices device
admin@ncs> show configuration devices <tab>
```

Quick look at the Ansible documentation for the modules:

```
ansible-doc -l | grep nso_
nso_action       Executes Cisco NSO actions and verifies output.
nso_config       Manage Cisco NSO configuration and service synchronization.
nso_query        Query data from Cisco NSO.
nso_show         Displays data from Cisco NSO.
nso_verify       Verifies Cisco NSO configuration.
```

# The `nso_action` module

You can now use the action module to bring NSO in sync with the network devices under management. The `sync-from.yaml` playbook uses the `nso_action` module to ask NSO to sync the configuration from all devices under management into the NSO data store.

```
ansible-playbook -v sync-from.yaml
```

# The `nso_show` and `nso_query` modules

Let's move on to use the show module to fetch configuration and operational data from the NSO data store and return it as a result of the operation. The module allows you to specify a path in NSO and return everything below that, with the option to exclude non-configuration (i.e. operational) data. The `device-show.yaml` playbook fetches all configuration from all devices, excludes operational data, displays it in JSON format. We add two more verbose options (`-v`) to make sure we get the output JSON nicely formatted.

```
ansible-playbook -vvv device-show.yaml
```

You can then use the query module on to use the show module to fetch configuration and operational data from the NSO data store and return it as a result of the operation. The `device-query.yaml` playbook uses an XPath query expression to fetch the name and NED type of all devices under management.

```
ansible-playbook -vvv device-query.yaml
```

# The `nso_verify` module

Now that NSO in in sync, we can start fetching data to use in our playbooks. The following commands shows you how to use `curl(1)` to fetch some configuration data from the `jnpr0` device through NSO. And then how to run the same data through the `json2yaml.py` tool producing the exact YAML output that can be used in the next step where we verify that the configuration is the same.

```
curl -s -u admin:admin -H "Accept: application/vnd.yang.data+json" http://localhost:8080/api/config/devices/device/jnpr0/config?deep
curl -s -u admin:admin -H "Accept: application/vnd.yang.data+json" http://localhost:8080/api/config/devices/device/jnpr0/config?deep | ../json2yaml.py
or with Python3
curl -s -u admin:admin -H "Accept: application/vnd.yang.data+json" http://localhost:8080/api/config/devices/device/jnpr0/config?deep | ../json2yaml3.py
```

Paste the output into the template playbook `verify-device-tmpl.yaml` and put it under the line with the device name. Remember to indent correctly so you don't break the YAML whitespace.

You can then run the verify playbook to verify that the configuration indeed has not changed.

```
ansible-playbook -v verify-device-tmpl.yaml -e device=jnpr0
```

You can now make a change the configuration and run the verify playbook again and look at the delta. First we change the configuration of `jnpr0` through the NSO CLI:

```
admin@ncs> configure
admin@ncs% set devices device jnpr0 config junos:configuration system domain-name baz.com
admin@ncs% commit
admin@ncs% exit
admin@ncs>
```

And then rerun the verify playbook to find the newly created deviation.

```
ansible-playbook -v verify-device-tmpl.yaml -e device=jnpr0
```

# The `nso_config` module

You can now create the corresponding configuration template and enforce the configuration. Paste your buffer into `configure-device-tmpl.yaml` under the line with device name (and remember the indentation again).

```
ansible-playbook -v configure-device-tmpl.yaml -e device=jnpr0
```

You can then recheck to make sure deviation is completely gone.

```
ansible-playbook -v verify-device-tmpl.yaml -e device=jnpr0
```

You can also remove configuration by using the `__state: absent` construct. We can use this feature to completely remove one of the name-servers from the configuration. The `delete-name-server.yaml` contains a play to do exactly this.

```
ansible-playbook -v delete-name-server.yaml -e device=jnpr0
```

That concludes this simple demo. Feel free to suggest additional steps through raising [github repo](https://github.com/NSO-developer/nso-ansible-demo) [issues](https://github.com/NSO-developer/nso-ansible-demo/issues), or even better through submitting pull requests.

# Resetting the runtime environment

Here are the steps to completely reset the runtime environment such that you can start fresh from the top of this demo.

```
ncs --stop
ncs-setup --reset
ncs-netsim stop
ncs-netsim delete-network
rm -rf packages state target scripts logs ncs-cdb storedstate README.netsim README.ncs ncs.conf
```

This can also be done using the `clean` target in the `Makefile`.
```
make clean
```

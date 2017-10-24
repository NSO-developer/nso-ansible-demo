# Introduction

This is an introduction on how to setup a small development environment with NSO, including a couple of simulated devices and exercise the three NSO modules ( nso_action, nso_verify, ans nso_configure).

# Preparing

You need to have both the NSO and Ansible environments setup, meaning you need $NSO_DIR to point to an NSO installation and have ansible-playbook(1) in your $PATH.

You will need to working directories, one for the NSO runtime files as well, and one for the Ansible playbook content.

If you are running the local fork of Ansible, you need to source `hacking/env-setup`. Please see `hacking/README.md` for more details.

## Setting up NSO

Use the ncs-netsim(1) tool to prepare to simulate a network consisting of three instances of simulated junos, cisco IOS-XE and cisco NX-OS respectively.

```
ncs-netsim create-network juniper-junos 3 jnpr
ncs-netsim add-to-network cisco-ios 3 xe
ncs-netsim start
```

This creates all the required files for starting the simulated instances and starts the devices.

```
ncs-netsim cli-c xe0
ncs-netsim cli jnpr0
```

Next is to set up the local NSO runtime environment and start it.

```
ncs-setup --dest .
ncs -v --foreground
```

Start the NSO CLI in a separate terminal.

```
ncs_cli -u admin
show configuration devices device
show configuration devices <tab>
```

Quick look at the documentation for the modules:

```
ansible-doc -l | grep nso_
ansible-doc nso_config
ansible-doc nso_verify
ansible-doc nso_action
```

And use Ansible to bring NSO in sync with the network:
```
ansible-playbook -vvv sync-from.yaml
```

Now that we are in sync, we can start fetching data from NSO to use in our playbooks. The following three commands shows you how to fetch some configuration data from the `jnpr0` device, how to run the same data through the json2yaml tool producing the exact YAML output that can be used in the next step.

```
curl -s -u admin:admin -H "Accept: application/vnd.yang.data+json" http://localhost:8080/api/config/devices/device/jnpr0/config?deep
curl -s -u admin:admin -H "Accept: application/vnd.yang.data+json" http://localhost:8080/api/config/devices/device/jnpr0/config?deep| ../json2yaml.py
```

Paste into verify-device-tmpl.yaml under line with device name (remember indent).

```
ansible-playbook -v verify-device-tmpl.yaml -e device=jnpr0
```

Change the config and look at the delta.

```
admin@ncs% set devices device jnpr0 config junos:configuration system domain-name baz.com
admin@ncs% commit
```

And then recheck to find the deviation.

```
ansible-playbook -v verify-device-tmpl.yaml -e device=jnpr0
```

Let's create the corresponding configuration template and enforce, paste buffer into configure-device-tmpl.yaml under line with device name (remember indent).

```
ansible-playbook -v configure-device-tmpl.yaml -e device=jnpr0
```

Recheck to make sure deviation is gone.

```
ansible-playbook -v verify-device-tmpl.yaml -e device=jnpr0
```

# Resetting the runtime environment
```
ncs --stop
ncs-setup --reset
ncs-netsim stop
ncs-netsim delete-network
rm -rf packages state target scripts logs ncs-cdb storedstate README.netsim README.ncs ncs.conf
```

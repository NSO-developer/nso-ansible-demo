netsim:
	ncs-netsim create-network juniper-junos 3 jnpr
	ncs-netsim add-to-network cisco-ios 3 xe
	ncs-netsim start

nso:
	ncs-setup --dest .
	ncs	
clean:
	-ncs --stop
	-ncs-setup --reset
	-ncs-netsim stop
	-ncs-netsim delete-network
	-rm -rf netsim packages state target scripts logs ncs-cdb storedstate README.netsim README.ncs ncs.conf

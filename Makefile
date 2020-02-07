ping:
	ansible all -m ping

setup:
	ansible-playbook ansible/setup.yml -i ansible/hosts

purge:
	ansible-playbook ansible/purge.yml -i ansible/hosts

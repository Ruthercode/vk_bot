ping:
	ansible all -m ping

setup:
	ansible-playbook ansible/setup.yml -i ansible/hosts

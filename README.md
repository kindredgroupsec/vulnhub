# Vulnhub

This project is intended to be a directory structure full of missconfigured or vulnerable applications running in Docker or Vagrant and examples
on how to exploit them. Intention is that you should find application and all the ways it can be exploitet documented with examples.

## Usage

Change directory to the application you want to experiment with and run any of these commands
depending if there is a docker-compose.yml file or Vagrantfile in the project.

```sh
docker-compose up -d
```

```sh
vagrant up --provision
```

Inside each folder there should be instructions or exploit code on how to experiment with each issue.


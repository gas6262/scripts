the CLI should be Python based, readable and modular so I or an agent can easily make changes intuitively without breaking other aspects of the app

It needs to also setup the new project in GCP. All APIs and apps should run in Cloudrun and everything should have a big focus on docker containerization and using the same port number for most HTTP requests to make everything simple. It should be highly opinionated. Everything should be dockerized out of the box.

It needs to go a bit further than just setting up the repo as well. It needs to set up and  all of the new infrastructure end to end. We need to expand a bit on the services schema. When I specify an API, it should be able to specify the stack for the API as well. Same for the worker and front end. 

I should also be able to set up a database (just as you enabled setting up services). If my db type is set to mongodb, it should set up the db inside of cluster 0 in my db using my mongodb Atlas credentials . inside cluster zero in my Atlas configuration. If it doesn't exist, then it should create it. If it does exist, then it should skip. All of the items need to be connected together such that I can do a full end to end hello world at the beginning. It should create a table in the new database called items with a basic schema such as just one column such as or name With just one entry in the table or a small set of entries using my user credentials.

For now lets only support the dev environment (and running locally using dev credentials)

Everything needs to work e2e and it should generate in order. When I have a mongodb, it needs to generate the new database using atlas if necessary via CLI. It should download any atlas CLI as necessary to do this. After generating the db (if it doesn't exist), it needs to generate a credentials or connections strings for the db which will be stored 2 places. On the local machine in the env files needed by the API or any downstream dependencies as well as in the GCP secret manager using the gcp CLI or any necessary command line tools The secrets should have the same name and there should be a commented section in the env file for all variables that live in the projects secret store. Then it should create the API using the stack I specify (default express + ORM based on db - mongoose for mongodb). Given the previously obtained credentials, the API should already be a hello world API with a GET /items endpoint that can obtain the items from the database. This should work on first load.

After creating the API, it should then create the corresponding docker files for the API which should map HTTP to port 80 as should all of my dockerfiles regardless of the original port of the app etc. Dockerfiles should contain the necessary requirements to build and run the app based on the stack (of the API or the app).

After creating the dockerfiles, it should generate the cloudbuild files for the API (or later the webb app) should be generated. All of the secrets that were needed will have been added to the secret store in GCP for the project and should be referenced in the .env file which should never be pushed to the repo since they will be injected by Cloudbuild as environment variables.

It then needs to generate terraform files for the necessary infra that can be rolled out. While there may be many terraform files, there should be only one Cloudbuild pipeline for the terraform files. So this should be explicitly listed in your folder breakdown that you had earlier.

After creating all of those files, it needs to connect everything to GCP. This will work on my local machine with my credentials. For example it needs to create the new Cloudrun instances and point it to the current repo. I've attached an example

Each service type should be using Cloudrun or Cloudrun functions. There may need to be a separate folder for all the yaml Cloudrun configurations for those services as well. Terraform should be referencing these files when rolling out the infrastructure

All of the integrations should be as modular as possible. Ideally, the webapp should not need to know the stack of the API. Just that it should exist. When creating the API, there should always be a datbase so when creating the API, we should pass the database credentials as an object prameter and each step should be independent in that way and could be represented as a graph of steps.

On the local machine, the apps may be run outside of docker for testing and development. webapps should ALWAYS run on localhost:3005 and APIs should always run on localhost:3006. They should not need to know much else about each other other than the endpoints needed (such as /items).

Workers should be based on Cloudrun. I should be able to specify a gpu type as well even for Cloud run in case the jobs include creating models etc.

Aside from the folders you listed originally, it also needs to create an agent.md or agents.md file that will provide the agent context on the new scaffold as well as a .claude, and a .vscode folder with all of the startup functions needed to run the projects locally such as running npm start.

Reuse CLIs as much as ppssible rather than scripting the steps themselves. For example, start with a react init script if one exists.

There may be many CLIs that are needed to run this. Therefore the cli needs to have 

The CLI needs to be usable and iterateble by an agen such as usage within a skill so build it accordingly

All necessary credentials needed to make the app work e2e should be stored in GCP secret manager. APIs and UIs should be containerized. When building thei

When specity an API, i also want to be able to specify the stack for the API and it should generate it consistently. For now let's start with the APIs based on express. If the database is mongodb, it should add a mongoose layer that connects to the 

I think its OK if everything doesn't work the first time. I will work locally with an agent to iterate on the CLI given a few test projects. The CLI needs to have a scaffold command that will do all of this. But I think the CLI also needs to have a test command that will for each service, test every aspect of it. e.g for the API, it should start a process to test the docker build, in parallel start a process to start the API and run the /items or dummy endpoint. It should be able to test the . It should be able to test the webapp very basically - get the webapp home page text, etc. 
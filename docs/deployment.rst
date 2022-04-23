Deployment
============================================

These instructions assume that you've set up your D-Codex project with dcodex-cookiecutter.

Deployment on Docker
--------------------

Instructions coming soon. For now, see https://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html


Deployment on AWS
--------------------

These instructions are correct as of the beginning of 2021. AWS might change their interface from time to time. Hopefully these instructions should still make sense even if some of the elements change over time. If you have suggestions on how to update or supplement these instructions, please let us know!
Additional instructions for setting up a cookiecutter-django project on AWS can be found on `Ben Lindsay's blog <https://benjlindsay.com/posts/deploying-a-cookiecutter-django-site-on-aws>`_.

0. Accounts and Permissions
You need an AWS account for completing the following instructions. It is possible for one user to set up the 'root' account and to have another user managing the deployment.
If that is the case, then the root user needs to create another user in the IAM console and give them permission 

1. Start an EC2 Instance
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Log in to the `AWS Management Console <https://console.aws.amazon.com/>`_. Select `EC2 <https://aws.amazon.com/ec2/?ec2-whats-new.sort-by=item.additionalFields.postDateTime&ec2-whats-new.sort-order=desc>`_ under 'services'. 
This will start a wizard to setup in EC2 instance. In the wizard, you can follow these steps:

* Select an `Amazon Machine Image (AMI) <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AMIs.html>`_ for the instance. I choose 'Amazon Linux 2 AMI' because it is eligible for the free tier. Other images will probably work similarly well.
* Then you need to choose an instance type. I choose t2.micro (- ECUs, 1 vCPUs, 2.5 GHz, -, 1 GiB memory, EBS only) which is eligible for the free tier.
* Then you will be asked to 'Configure Instance Details'. The defaults should be fine.
* Next it will ask you to 'Add Storage'. The defaults here are fine.
* Next it will ask you to 'Add Tags'. That isn't necessary at this stage.
* Next it will ask you to 'Configure Security Group'. You need click the 'Add Rule' button to add the HTTP and then the HTTPS protocols. It should automatically select the correct ports (i.e. 80 and 443).
* Then it will show you a summary of your decisions and let you review your choices. You are now able to click the 'Launch' button.
* If you haven't created an instance previously, it will prompt you to download a new key pair. Save it in your ~/.ssh directory. Make sure you keep it secret and never check it in to a repository. This key needs to be only readable by you so you may need to change the permissions. e.g. :code:`chmod 600 ~/.ssh/<name of key>.pem`.
* You can now click the 'Launch Instances' button. The instance will then be launched. It may take a short time to fire up.


2. Create an Elastic IP
^^^^^^^^^^^^^^^^^^^^^^^^^^^

You need an IP address to get to your EC2 instance. The dashboard should show you an IP address for your EC2 instance but this one might change in the future. You can set up an 'Elastic IP Address' to point to your instance over its lifetime. 
This IP might change. At the time of writing, a single elastic IP is available from AWS at no charge.

* On the navigation panel on the left, go down to 'Network & Security' and choose 'Elastic IPs'. 
* Click the button 'Allocate Elastic IP address'.
* By default it will have selected to choose an IP address from Amazon's IPv4 pool which should be fine in most circumstances.
* Click 'Allocate' and it should give you a public IP address.
* On the 'Actions' dropdown bar, select 'Associate Elastic IP address'.
* Then find the EC2 instance in the 'Instance' select box and press the 'Associate' button.


3. Set up a domain name
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Now that we have a fixed IP address, we need to associate it with a domain name. At your domain name provider (which could be AWS, GoDaddy, Google Domains, or Freenom etc.), create 'A' records that point a domain name (and a 'www' subdomain if you like) to your new Elastic IP address.


4. Create an S3 bucket
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Now we need to create an S3 storage bucket that we will set up for the media and static files for use in dcodex.

Instructions coming soon. For now see: https://docs.aws.amazon.com/AmazonS3/latest/user-guide/create-bucket.html.


5. Create an IAM role
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Now we need to create an Identity and Access Management (IAM) role for the EC2 instance to access the S3 storage bucket.

* Click on 'Services' and find IAM.
* Find 'Roles' on the left navigation sidebar.
* Click the 'Create Role' button.
* Make sure that the button 'AWS Service' is selected and then choose EC2 (which might be under 'Common Use Cases'). Then click the 'Next: Permissions' button.
* Put the term :code:`AmazonS3FullAccess` in the filter, select the policy with that name and the 'Next' button.
* You can skip the option to add tags.
* Give this role a name such as :code:`S3_Access` and then click 'Create role'.

We now need to give add this role to the EC2 instance:

* Go back to the EC2 dashboard and select the checkbox for the instance you created.
* On the 'Actions' dropdown bar, choose 'Security' and then 'Modify IAM role'.
* Choose the IAM role you recently created (called :code:`S3_Access` or whatever you called it) and then click 'Save'.

6. Configuration
^^^^^^^^^^^^^^^^^^^^

When you ran dcodex-cookiecutter to generate a D-Codex project, if would have created a folder at :code:`.envs/.production`. 
This includes environment variables used to configure your project in production.
By default, this will be ignored by git and it should never be added to a respository.
You need to add the name of your S3 bucket there.
Find the line with :code:`DJANGO_AWS_STORAGE_BUCKET_NAME` and add the name of your bucket: ::

    DJANGO_AWS_STORAGE_BUCKET_NAME=my_bucket_name

.. note::

    You don't have to set the :code:`DJANGO_AWS_ACCESS_KEY_ID` and :code:`DJANGO_AWS_SECRET_ACCESS_KEY` variables because you set up the IAM Role in the previous step.
    For further information, see the note in `django-cookiecutter <https://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html#optional-use-aws-iam-role-for-ec2-instance>`_ and `django-storages <https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html>`_.


7. Install Docker on your EC2 Instance
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can now log in to your EC2 instance like this: ::

    $ ssh -i ~/.ssh/<name of key>.pem ec2-user@<your domain name>

.. note::

    The username for everyone is exactly :code:`ec2-user`.

You can make this simpler for next time by adding an entry in your :code:`~/.ssh/config`: ::

    Host ec2instance
            HostName <your domain name>
            User ec2-user
            IdentityFile ~/.ssh/<name of key>.pem

You can set the name of the 'host' (here :code:`ec2instance`) to be any shortcut you like. Then you should be able to simply log in with the command: ::

    ssh ec2instance

Install Docker with the following commands: ::

    sudo yum update -y
    sudo yum install -y docker
    sudo service docker start
    sudo yum install -y python3-devel
    sudo pip3 install docker-compose

This command will enable you to use Docker without needed to sudo: ::

    sudo usermod -aG docker ec2-user

.. note::

    For this to work, you might need to log out and log back in again.


Test your installation with the following command: ::

    docker ps

If docker is installed and you have access, then you should see an empty list of containers list this: ::

    CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES

8. Copy the files
^^^^^^^^^^^^^^^^^^^

Now you can copy your files ot the EC2 instance using rsync. Just go to the project you created using dcodex-cookiecutter and run the command ::

    rsync -av --exclude='.git/' . ec2instance:~/app/

.. note ::
    
    Here :code:`ec2instance` is the shortcut host in your :code:`~/.ssh/config` file.

.. note ::

    The command will exclude your files in `.git`. You might want to also exclude transferring a local media directory if it exists since these will be going to the S3 bucket.

9. Deploy!
^^^^^^^^^^^^^^^

Now you can ssh back in to your EC2 instance and go to your new :code:`app` directory: ::

    ssh ec2instance
    cd app

From here you should finally be able to deploy your dcodex project: ::

    docker-compose -f production.yml up -d --no-deps --build


11. Setup a blank database
^^^^^^^^^^^^^^^^^^^^^^^^^^

If you are importing an existing database, skip to the next section. Otherwise, if you are starting from a blank database, then you just need to perform a migration: ::

    docker-compose -f production.yml run --rm django python manage.py migrate

If the dcodex apps you are using need any database fixtures installed, then  you can to that now. e.g. To import the basic Bible verses into dcodex-bible, run this command::

    docker-compose -f production.yml run --rm django python manage.py import_bibleverses

12. Importing an existing database
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you have a database to import, then copy the database file from your local computer to the EC2 instance using scp. Here it is assumed that it is called MyDatabase.sql.gz ::

    scp MyDatabase.sql.gz ec2instance:.

Then find the ID of the PosgreSQL container on the EC2 instance. This is can be stored in an environment variable like this: ::

    POSTGRES_CONTAINER_ID=$(docker container ls | grep postgres | awk '{print $1}')
    echo $POSTGRES_CONTAINER_ID

Now copy the database file to the backups directory in the PostgreSQL container: ::

    docker cp ~/MyDatabase.sql.gz $POSTGRES_CONTAINER_ID:/backups/

Bring down the site with this command: ::

    docker-compose -f production.yml down

Start up just the PostgreSQL container ::

    docker-compose -f production.yml up -d postgres

Import the backup with this command: ::

    docker-compose -f production.yml exec postgres restore MyDatabase.sql.gz

Now bring all the containers back up with ::

    docker-compose -f production.yml up -d

13. Visit your site
^^^^^^^^^^^^^^^^^^^

Your project should be accessible through your domain now! If there is an error, you can check the logs like this::

    docker-compose -f production.yml logs

Please let me know if you have issues and I will try to help.


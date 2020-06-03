#uncomment the below line while running for the first time
#sudo docker pull postgres
#in the below line provide path to where you want the postgres volume to be stored
mkdir -p $HOME/path/to/volumes/postgres
sudo docker run  --name docker-postgres -e POSTGRES_PASSWORD=docker -d -p 5432:5432 -v $HOME/path/to/volumes/postgres:/var/lib/postgresql/data -v /home/path/to/sql_scripts:/root/scripts/ postgres
echo "Container is running. To connect run the connect script"

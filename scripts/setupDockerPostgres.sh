
#sudo docker pull postgres
mkdir -p $HOME/mydocs/projects/v2/volumes/postgres
sudo docker run  --name docker-postgres -e POSTGRES_PASSWORD=docker -d -p 5432:5432 -v $HOME/mydocs/projects/v2/volumes/postgres:/var/lib/postgresql/data -v /home/ghost/mydocs/projects/v2/sql_scripts:/root/scripts/ postgres
echo "Container is running. To connect run the connect script"

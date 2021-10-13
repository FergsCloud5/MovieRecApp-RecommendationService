# Cloud5 Recommendation Service Repo
(More details to come soon!)

## Connection Info:
### AWS EC2
EC2 Instance Public Address: ec2-18-119-118-50.us-east-2.compute.amazonaws.com:5000  
(Make sure you include :5000 for the correct port number!)

### AWS RDS (MySQL):
export DBHOST=database.czthk9zzx7f7.us-east-1.rds.amazonaws.com  
export DBUSER=dbuser  
export DBPASSWORD=dbuserdbuser  

#### Quick Note: This is hosted on my AWS Student account and I have to have a AWS student session running for my RDS instance to be running. Will try to migrate this out to a personal RDS instance to ease of use. Will also upload a SQL creation script to entire DB so that others can create their own RDS instance running the same way. As of right now from my testing, it seems like I am able to access it with the AWS student session closed, but I haven't tested for an extended period of time.  


### NLP Model Used for Recommendations:
Our recommendation microservice utilizes a NLP model to help recommend relevant movies. While our project is much more than the NLP model, the original NLP model that we use for our recommendations is available in the following repo:  
https://github.com/kishan0725/AJAX-Movie-Recommendation-System-with-Sentiment-Analysis

#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <sys/types.h>
#include <time.h> 
#include <netdb.h>
#include <pthread.h>

pthread_t tid[2];

void *server(){
	pthread_t id = pthread_self();
	//this is server
	if (pthread_equal(id, tid[0])){
		int listenfd = 0, connfd = 0;
    		struct sockaddr_in serv_addr; 

    		char sendBuff[1025];
    		char text[1024];
    		char name[10] = "GL";
    		time_t ticks; 

    		listenfd = socket(AF_INET, SOCK_STREAM, 0);
    		memset(&serv_addr, '0', sizeof(serv_addr));
    		memset(sendBuff, '0', sizeof(sendBuff)); 

   		serv_addr.sin_family = AF_INET;
    		serv_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    		serv_addr.sin_port = htons(5000); 

    		bind(listenfd, (struct sockaddr*)&serv_addr, sizeof(serv_addr)); 

    		listen(listenfd, 10); 

    		while(1)
    		{
        		connfd = accept(listenfd, (struct sockaddr*)NULL, NULL); 

        		ticks = time(NULL);
        		memset(text, '0',sizeof(text));
        		gets(text);
        		//memcpy(sendBuff, text, strlen(text)+1);
        		//printf("sendBuff = %s\n", sendBuff);
        		snprintf(sendBuff, sizeof(sendBuff), "[From %.24s] %.24s : %.30s\r\n", name, ctime(&ticks), text);
        		write(connfd, sendBuff, strlen(sendBuff)); 

        		close(connfd);
        		sleep(1);
    		 }
	}
	}


void *client(){
	int sockfd = 0, n = 0;
    	char recvBuff[1024];
    	struct sockaddr_in serv_addr; 
	/*
    	if(argc != 2)
    	{
       		printf("\n Usage: %s <ip of server> \n",argv[0]);
        	return 1;
    	} 
	*/

	while(1){
    	memset(recvBuff, '0',sizeof(recvBuff));
   	if((sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0)
    	{
        	printf("\n Error : Could not create socket \n");
    	} 
	
    	memset(&serv_addr, '0', sizeof(serv_addr)); 

    	serv_addr.sin_family = AF_INET;
    	serv_addr.sin_port = htons(5000); 
    	serv_addr.sin_addr.s_addr = inet_addr("192.168.1.174");

    	if( connect(sockfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0)
    	{
       		printf("\n Error : Connect Failed \n");
       		sleep(2);
    	} 

    	while ( (n = read(sockfd, recvBuff, sizeof(recvBuff)-1)) > 0)
    	{
        	recvBuff[n] = 0;
        	if(fputs(recvBuff, stdout) == EOF)
        	{
            		printf("\n Error : Fputs error\n");
        	}
    	} 

    	if(n < 0)
    	{
        	printf("\n Read error \n");
    	} 
    	}
	}

int main(){
	int i = 0;
	int err[2] = {0};
	void *status;
	err[1] = pthread_create(&(tid[0]), NULL, &server, NULL);
	err[2] = pthread_create(&(tid[1]), NULL, &client, NULL);
	pthread_join(tid[0], &status);
	return 0;
}

#include <stdio.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <time.h>
#include <errno.h>
#include <signal.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/time.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define BUFSIZE 1024

/*
 * author: Tireless
 * by time : 2022-10-15
 * by tool : CLion
 * by language : C
 */

typedef struct {
    char *username;
    char *password;
    char *encrypted_password;
} UserInfo;


int http_post(char *method,char *url,UserInfo *user , int sclient){


    char str1[4096], str2[4096], buf[BUFSIZE], *str;

    int ret;


    //创建socket
    sclient = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (sclient < 0)
    {
        printf("invalid socket !");
        return -1;
    }
    struct sockaddr_in serAddr;
    serAddr.sin_family = AF_INET;
    serAddr.sin_port = htons(80);

    serAddr.sin_addr.s_addr = inet_addr("172.16.154.130"); //这里是认证页面的ip地址，请修改

    if (connect(sclient, (struct sockaddr *)&serAddr, sizeof(serAddr)) < 0){
        printf("连接到服务器失败,connect error!\n");
        return -1;
    }


    sprintf(str2,"{\"action\":\"login\",\"username\":\"%s\",\"password\":\"%s\",\"type\":2,\"n\":117,\"drop\":0,\"pop\":0,\"mbytes\":0,\"minutes\":0,\"ac_id\":1}",user->username,user->encrypted_password);

    str = (char *)malloc(128);

    memset(str1, 0, 4096);
    sprintf(str1, "%s %s HTTP/1.1\r\n", method, url);
    strcat(str1, "Host: 172.16.154.130\r\n"); //这里是认证页面的ip地址，请修改
    strcat(str1, "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36\r\n");
    strcat(str1, "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8\r\n");
    strcat(str1, "Accept-Encoding: gzip, deflate\r\n");
    strcat(str1, "Content-Type: application/json;charset=UTF-8\r\n");
    strcat(str1, "Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2\r\n");
    strcat(str1, "Connection: clone\r\n");
    sprintf(str, "Content-Length: %d\r\n", (int )strlen(str2));

    strcat(str1, str);
    strcat(str1,"\r\n");
    strcat(str1, str2);

    strcat(str1, "\r\n\r\n");

    ret = write(sclient,str1,strlen(str1));

    if (ret < 0) {
        printf("发送失败！错误代码是%d，错误信息是'%s'\n",errno, strerror(errno));
        return -1;
    }

    //接收服务器传回的数据
    char szBuffer[BUFSIZE * 3] = {0};
    read(sclient, szBuffer, BUFSIZE * 3);

    if(strstr(szBuffer,"login_ok") != NULL){
        printf("login success\n");
    }else{
        printf("login failed\n");
    }
    //关闭套接字
    close(sclient);

    return 0;
}



char* encryptPassword(char *password){
    int paw_length = strlen(password);
    char *pad = password;
    char *result =(char *)malloc(paw_length * 2 + 1) ;
    int i,idx;
    char char_c, char_r;

//    初始化，将result中的每个元素都置为0，至关重要
    memset(result, 0, paw_length * 2 + 1);

    char  column_key[8] = {0, 0, 'd', 'c', 'j', 'i', 'h', 'g'};
    char  row_key[10][16] = {
            {'6', '7', '8', '9', ':', ';', '<', '=', '>', '?', '@', 'A', 'B', 'C', 'D', 'E'},
            {'?', '>', 'A', '@', 'C', 'B', 'E', 'D', '7', '6', '9', '8', ';', ':', '=', '<'},
            {'>', '?', '@', 'A', 'B', 'C', 'D', 'E', '6', '7', '8', '9', ':', ';', '<', '='},
            {'=', '<', ';', ':', '9', '8', '7', '6', 'E', 'D', 'C', 'B', 'A', '@', '?', '>'},
            {'<', '=', ':', ';', '8', '9', '6', '7', 'D', 'E', 'B', 'C', '@', 'A', '>', '?'},
            {';', ':', '=', '<', '7', '6', '9', '8', 'C', 'B', 'E', 'D', '?', '>', 'A', '@'},
            {':', ';', '<', '=', '6', '7', '8', '9', 'B', 'C', 'D', 'E', '>', '?', '@', 'A'},
            {'9', '8', '7', '6', '=', '<', ';', ':', 'A', '@', '?', '>', 'E', 'D', 'B', 'C'},
            {'8', '9', '6', '7', '<', '=', ':', ';', '@', 'A', '>', '?', 'D', 'E', 'B', 'C'},
            {'7', '6', '8', '9', ';', ':', '=', '<', '?', '>', 'A', '@', 'C', 'B', 'D', 'E'},

    };

    idx = 0;
    for(i = 0; i < paw_length; i++) {
        char_c = column_key[pad[i] >> 4];
        char_r = row_key[i % 10][pad[i] & 0xf];
        if(i % 2 != 0){
            result[idx] = char_c;
            result[idx+1] = char_r;
        } else{
            result[idx] = char_r;
            result[idx+1] = char_c;
        }
        idx += 2;
    }

    return result;
}

int main(){
    int sclient;
    UserInfo *user;

    user = (UserInfo *) malloc(sizeof (UserInfo));

    char *online_url = "/cgi-bin/rad_user_info";
    char *login_url = "/cgi-bin/srun_portal";

    char *username = "登录账号";
    char *password = "登录密码";
    user->username = username;
    user->password = password;
    user->encrypted_password = encryptPassword(password);

    while(1){
        http_post("POST", login_url,user, sclient);
        sleep(1);
    }

}


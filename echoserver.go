package main

import (
	"flag"
	"net/http"
	"github.com/gorilla/websocket"
	"strconv"
	"bufio"
	"fmt"
)

var port int
var servername string

func WSServer(w http.ResponseWriter, req *http.Request)  {
	var upgrader = websocket.Upgrader{
      ReadBufferSize:  64,
      WriteBufferSize: 64,
  	}
  	conn, err := upgrader.Upgrade(w, req, nil)
  	if err != nil {
  		fmt.Println("ERROR:"+err.Error())
  		return
  	}
  	for {
	     messageType, r, err := conn.NextReader()
	     reader := bufio.NewReader(r)
	     b, err := reader.ReadBytes('\n')

	     response := []byte("ECHO FROM "+servername+":"+string(b))
	     if err != nil {
	     	fmt.Println("ERROR:"+err.Error())
	        return
	     }
	     // w, err := conn.NextWriter(messageType)
	     // if err != nil {
	     // 	fmt.Println("ERROR:"+err.Error())
	     //    return 
	     // }
	     if err := conn.WriteMessage(messageType, response); err != nil {
	     	fmt.Println("ERROR:"+err.Error())
	         return 
	     }
     }
}


func main(){
	flag.IntVar(&port, "p", 7000, "port")
	flag.StringVar(&servername, "n", "server1", "name")
	port_str := strconv.Itoa(port)
	http.HandleFunc("/ws", WSServer)
	http.ListenAndServe("0.0.0.0:" + port_str , nil)
}

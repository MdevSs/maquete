String cmd;
int sec;
void setup() {
  Serial.begin(9600);
  
  // G
  pinMode(2, OUTPUT);

  // Y
  pinMode(3, OUTPUT);
  
  // R
  pinMode(4, OUTPUT);

  // G
  pinMode(7, OUTPUT);

  // Y
  pinMode(6, OUTPUT);
  
  // R
  pinMode(5, OUTPUT);
}

void loop() {
    //digitalWrite(2,1);
    //digitalWrite(3,1);
    //digitalWrite(4,1);
    //digitalWrite(5,1);
    //digitalWrite(6,1);
    //digitalWrite(7,1);
    if (Serial.available()) {
    String msg = Serial.readStringUntil('\n');  // ex: "1R15"

      if (msg.length() >= 2) {
        char semaforo = msg.charAt(0);
        char cor = msg.charAt(1);

        // resto da string Ã© o tempo em texto â†’ converter para int
        //int tempo = msg.substring(2).toInt(); 
        // ex: substring(2) = "15"

        //Serial.println("===== RECEBIDO =====");
        //Serial.print("Semaforo: ");
        //Serial.println(semaforo);
        //Serial.print("Cor: ");
        //Serial.println(cor);
        //Serial.print("Tempo (int): ");
        //Serial.println(tempo);
        if (semaforo == '1') {
            if (cor == 'G') {
                digitalWrite(7,0);//2R
                digitalWrite(5,0);//2G
                digitalWrite(6,1);//2Y
                delay(3000);
                digitalWrite(6,0);//2Y
                digitalWrite(7,1);//2R
                digitalWrite(5,0);//2G
                digitalWrite(3,0);//1Y
                digitalWrite(4,0);//4R
                digitalWrite(2,1);//2G


                 
            }
            if (cor == 'R') {
                digitalWrite(7,1);
                digitalWrite(6,0);
                digitalWrite(5,0);
                digitalWrite(2,0);//1G
                digitalWrite(4,0);//1R
                digitalWrite(3,1);//1Y
                delay(3000);
                digitalWrite(3,0);//1Y
                digitalWrite(4,1);//1R
                digitalWrite(2,0);//1G
                digitalWrite(5,1);//2G
                digitalWrite(6,0);//2Y
                digitalWrite(7,0);//2R
            }
        }else{
                digitalWrite(7,1);
                digitalWrite(6,0);
                digitalWrite(5,0);
                digitalWrite(2,0);//1G
                digitalWrite(4,1);//1R
                digitalWrite(3,0);//1Y  
        }
      }      
    }
}

  // if(Serial.available() > 0){
    
  //   cmd = Serial.readStringUntil('\n');
  //   Serial.println(cmd);
  
//   }
//   if(cmd == "1R"){
//     digitalWrite(2,0);
//     digitalWrite(3,0);
//     digitalWrite(4,1); 
//     if(Serial.available() > 0){
    
//       sec = Serial.parseInt();
//       Serial.println(sec);
//       delay(sec);
//       digitalWrite(4,0); 
//     } 
//   }
//   if(cmd == "1G"){
//     digitalWrite(2,1);
//     digitalWrite(3,0);
//     digitalWrite(4,0);  
//   }
//   if(cmd == "1Y"){
//     digitalWrite(2,0);
//     digitalWrite(3,1);
//     digitalWrite(4,0);  
//   }
// }

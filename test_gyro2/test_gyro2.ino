#include<Wire.h>
#include <math.h>
#include <Servo.h>
#define NumData 7
#define pi      3.1415926535897932384626433832795  
#define MPU     0x68
int position1 = 0;
int position2 = 0;
Servo servo1, servo2;

// Pinout 
/*
  VCC -> 3.3 V / 5 V (péférable)
  GND -> GND
  SCL -> A5
  SDA -> A4
  
  XDA -> NC (non connecté)
  XCL -> NC 
  ADO -> NC
  INT -> NC
 */
 
int  GyAccTemp[NumData];
int  GATCorr[NumData]={0,0,0,0,0,0,0};
//int  GATCorr[NumData]={-950,-300,0,-1600,480,170,210};

double PitchRoll[3];

void setup()
{
  // Init module GY-512 
  Wire.begin();
  Wire.beginTransmission(MPU);
  Wire.write(0x6B);
  Wire.write(0);
  Wire.endTransmission(true);
  servo1.attach(3);
  servo2.attach(5);

  // Init port série 
  Serial.begin(9600);
}
void loop()
{
  // Lecture du capteur 
  ReadGY521( GyAccTemp, GATCorr);
  
  // Conversion pitch/Roll / Yaw
  ComputeAngle(GyAccTemp, PitchRoll);

  // Affichage dans le port série Roll/Pitch/ Yaw en °

  
  Serial.print(PitchRoll[0]); Serial.print(",");
  Serial.print(PitchRoll[1]); Serial.print(",");
  Serial.println(PitchRoll[2]); //Serial.print(";");


  servos(PitchRoll[0], PitchRoll[1]);

  delay(100);
  

  
}



// Lecture des données des capteurs 
void ReadGY521( int *GyAccTempp, int *GATCorrr)
{
  // Init du module GY-521
  Wire.beginTransmission(MPU);
  Wire.write(0x3B);
  Wire.endTransmission(false);
  Wire.requestFrom(MPU,14,true);

  // Lecture des données (3 axes accéléromètre + température + 3 axes gyroscope
  for  (int i=0;i<NumData;i++)
  {
    if(i!=3)
    {
      GyAccTempp[i]=(Wire.read()<<8|Wire.read()) + GATCorrr[i];
    }
    else
    {
      GyAccTempp[i]=(Wire.read()<<8|Wire.read()) + GATCorrr[i];
      GyAccTempp[i] = GyAccTempp[i]/340 + 36.53;
    }
  }
}

//Conversion des données accéléromètre en pitch/roll/yaw
void ComputeAngle(int *GyAccTempp,  double *PitchRol)
{
  double x = GyAccTempp[0];
  double y = GyAccTempp[1];
  double z = GyAccTempp[2];

  PitchRol[0] = atan(x/sqrt((y*y) + (z*z))); //  pitch 
  PitchRol[1] = atan(y/sqrt((x*x) + (z*z))); // roll
  PitchRol[2] = atan(z/sqrt((x*x) + (y*y))); // pitch
  
  //Conversion Radian en degré
  PitchRol[0] = PitchRol[0] * (180.0/pi);
  PitchRol[1] = PitchRol[1] * (180.0/pi) ;
  PitchRol[2] = PitchRol[2] * (180.0/pi) ;
}

void servos(int pitch, int roll){
  servo1.write(pitch);
  servo2.write(roll);

  /*
  for(int i = position1; i <= pitch; i++){
    servo1.write(i);
  }
  for(int i = position1; i >= pitch; i--){
    servo1.write(i);
  }
  for(int i = position2; i >= roll; i--){
    servo2.write(i);
  }
    for(int i = position2; i >= roll; i--){
    servo2.write(i);
  }*/
  
  
}

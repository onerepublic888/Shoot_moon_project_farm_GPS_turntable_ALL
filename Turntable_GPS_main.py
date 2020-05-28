import csv
from math import sin, cos, radians, sqrt , pi, atan
#from time import sleep
import time, datetime
import paho.mqtt.publish as publish

from GPS_Threading_new2 import GPS_Rx                                              # gps thread 
from Datarate_Threading import Datarate_show 
#from Microtike_60G_Read_SSH import SSH                                   # datarate thread
import serial
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
#-----------------------------------------------------initial  Variable ---------------------------------------------#p
host = "192.168.88.250"

topic = "Client/Datarate"
client_id = "Datarate"

topic_1 = "Client/Distance"
client_id_1 = "Distance"

topic_2 = "Client/Height"
client_id_2 = "Height"

pos_x = [0]
pos_y = [0]
 
#Ground_Truth = [25.017808, 121.544543]                                         #MD402
Ground_Truth = [25.019734, 121.534560]                                     # testFile_name = '20190320_test'
#the = float(input("Update angle:"))
the = float(0)
Dis = input("Input your Distance:")
date = datetime.datetime.now()
File_name = './Outdoor/GPS_'+ '_' +str(Dis) + 'm'
#File_name_for_save = str(date.month) + '_' + str(date.day) + '_' + str(Dis) + 'm'
lat_factor = 1.1119
lon_factor = 1.00772
#---------------------------------------def lat_lon_H_2_XYZ----------------------------------------#
print(File_name)
def lat_lon_H_2_XYZ(sig):
    lat = float(sig[0])                                     # latitude = theta
    lon = float(sig[1])                                     # longtitude = phi
    he =  float(sig[2])                                                      # height
#    sat = (int(sig[3]))                                                         # 衛星數量                
#    print('in the fuckfuck lat lon',lat,lon)
    lat_R = lat
    lon_R = lon
    lon= radians((lon))
    lat= radians((lat))
    R = 6378137    
                                                        # 地球半徑
    X = (R+he)*cos(lat)*cos(lon)                                                # GPS的球座標轉直角坐標
    Y = (R+he)*cos(lat)*sin(lon)
    Z = (R+he)*sin(lat)
    return X,Y,Z,he,(lat_R),(lon_R)
 
#--------------------------------------def  XYZ_2_ENU---------------------------------------------------#
def XYZ_2_ENU(X,Y,Z,lat,lon,he):
    X_l, Y_l, Z_l =  -3023541.1892212625, 4929140.089529915 ,2691235.417698868  # server position from receive GPS first value 
    X_ecef = np.array([X-X_l,Y-Y_l,Z-Z_l])                                      # ECEF coordinate system
    Rz = np.array([cos(radians(lon)),sin(radians(lon)),0,-sin(radians(lon)),cos(radians(lon)),0,0,0,1])
    Ry = np.array([cos(radians(90-lat)),0,-sin(radians(90-lat)),0,1,0,sin(radians(90-lat)),0,cos(radians(90-lat))])
    X_ecef = np.reshape(X_ecef,(3,1))
    Rz = np.reshape(Rz,(3,3))
    Ry = np.reshape(Ry,(3,3))
    
    return np.dot(Ry,np.dot(Rz,X_ecef))

#-----------------------------------------------def animate------------------------------------------#
fig = plt.figure()
#ax1 = fig.add_subplot(2, 1, 1)
ax1 = fig.add_subplot(1, 1, 1)
#ax2 = fig.add_subplot(2, 1, 2)
def animate(i):
    graph_data = open('example.txt','r').read()
    lines = graph_data.split('\n')
#    print('11',lines)
    xs,ys = [], []
    annot_x = [0]
    annot_y = [0]
    x_angle, y_angle = [], []
#    plt_time, plt_DR, plt_eve, plt_azi = [], [], [], []
    for line in lines:
#        print('line ---',line.split(','),len(line.split(',')))
        if len(line.split(',')) == 2:
#            x, y, time, dr, eve, azi = line.split(',')
            x, y = line.split(',')
            xs.append(float(x))
            ys.append(float(y))
#            print(x,y)
            annot_x.append(float(x))
            annot_y.append(float(y))
            x_angle.append(float(x))
            y_angle.append(float(y))
#            plt_time.append(float(time))
#            plt_DR.append(float(dr))
#            plt_eve.append(float(eve))
#            plt_azi.append(float(azi))
#            print('plot',x,y,plt_time, plt_DR, plt_eve, plt_azi)
#            print('plot',x,y)
    ax1.clear()
    ax1.scatter(0,  0, c = 'k',marker='^', s = 250, label = 'Anchor')
    ax1.scatter(x_angle, y_angle, c = 'dodgerblue', marker= 'o', s=225, label = 'Quadrotor')
    ax1.set_xlabel('x [m]',fontsize = 14)
    ax1.set_ylabel('y [m]',fontsize = 14)
    ax1.set_xticks(np.arange(-100, 650, 50))
    ax1.set_yticks(np.arange(-50, 550, 50))
    ax1.grid()
    ax1.set_title('Quadrotor Position',fontsize = 18)
    ax1.legend(loc='upper right')
#    ax3 = ax2.twinx()
#    line, = ax2.plot(plt_time, plt_DR, color = 'blue',maker = 's', label = 'Data rate')  #maker = 'o',
#    line2, = ax3.plot(plt_time, plt_eve, color = 'red',maker = 's', label = 'Elevation angle') 
#    line3, = ax3.plot(plt_time, plt_azi, color = 'green',maker = 's', label = 'Azimuth angle')     
#    line, = ax2.plot(plt_time, plt_DR, label = 'Data rate')  #maker = 'o',
#    line2, = ax3.plot(plt_time, plt_eve,  label = 'Elevation angle') 
#    line3, = ax3.plot(plt_time, plt_azi, label = 'Azimuth angle')
#    ax2.legend(handles=[line], loc='best', bbox_to_anchor=(1, 0.68))
#    ax3.legend(handles=[line2, line3], loc='upper right')
#    ax2.set_xlabel('Time [s]', fontsize = 14)
#    ax2.set_ylabel('Date Rate [Mbps]', fontsize = 14)
#    ax3.set_ylabel('Angle [degree]', fontsize = 14)
#    ax2.set_xlim(0, 700)
#    ax2.set_ylim(0, 900)
#    ax3.set_ylim(0, 300)
#
#    ax2.grid()
#    ax3.grid()
    
#    tkw = dict(size=4, width=1.5)
#    ax2.tick_params(axis='x', **tkw)
#    ax2.tick_params(axis='y', colors=line.get_color(), **tkw)
#    ax2.tick_params(axis='y', colors=line2.get_color(), **tkw)
#    ax2.tick_params(axis='y', colors=line3.get_color(), **tkw)
#    lines = [line, line2, line3]
#    ax2.legend(lines, [l.get_label() for l in lines])
#    ax2.set_title('Outdoor measurement (GPS)', fontsize = 18)
    
ani = animation.FuncAnimation(fig, animate, interval=1000)  # must add ani



#-----------------------------------------------def spherical coordinate system------------------------------------------#
def sph_coordinate(x,y,z):  
    r = (x**2+y**2+z**2)**0.5                                                   # r = 
#    phi = (atan(y/x))/3.14*180                               # initial elevation angle 180 =>:Y72000
    if y > 0 and x > 0:
        phi = 180 + (atan(abs(x/y))*180/pi)       #90+
    elif y < 0 and x > 0:
        phi = 270+((atan(abs(y/x))*180)/pi)         #180+
    elif y < 0 and x < 0:
        phi = (atan(abs(x/y))*180)/pi      #+270
    elif y > 0 and x < 0:
        phi = 90 + (atan(abs(y/x))*180)/pi       #0
    theta = (atan((z/(x**2+y**2)**0.5)))/3.14*180         # initial azimuth angle 90 =>:X36000
#    if z > 0:
#        theta = 180-(atan((z/(x**2+y**2)**0.5)))/3.14*180
#    elif z < 0:
#        theta = 180+(atan((z/(x**2+y**2)**0.5)))/3.14*180
    return r,theta,phi   

#------------------------------------------------def main-------------------------------------------------#
def main():
    ser_motor = serial.Serial('COM3', 9600, timeout= 0.5)                       # Turntable 的 com port
    motor_degree = 0.0025                                                       #
    azimuth_angle_old = 0
    elevation_angle_old = 0
    azimuth_angle_num_update = 0
    elevation_angle_num_update = 0
    Lat_Lon_alt_Update = ['','','']
#    print("Motor Initial to 0 degree")
    # ser_motor.write(':X0,'.encode())
    print("Turntable Initialize")
    GPS_port = GPS_Rx() 
    Datarate = Datarate_show()
    GPS_port.start()
    Datarate.start()
#    ssh = SSH()
#    ssh.start()
    time.sleep(1.)
    time.sleep(2.)
    Datarate.resume()
    print("Start!")
    Start = time.time()
    try:
        while True:
            time.sleep(0.1) 
            try:
                Lat_Lon_alt_Update = [GPS_port.GPS_array[0],GPS_port.GPS_array[1],GPS_port.GPS_array[2]]        #從GPS threading 得到經緯度
                X ,Y ,Z , alt , lat, lon = lat_lon_H_2_XYZ(GPS_port.GPS_array)                                  #經緯度轉成local座標
                n , e , u = XYZ_2_ENU(X,Y,Z,lat,lon,alt)                                                        #無人機座標轉成以基站當原點之向量
                distance, elevation_angle, azimuth_angle = sph_coordinate(e, -n, u)                             #xyz to r theta phi
                 
                azimuth_angle_update = abs(azimuth_angle_old - azimuth_angle)
                elevation_angle_update = abs(elevation_angle_old - elevation_angle)                
                azimuth_angle_num = int(round(azimuth_angle,2)/motor_degree)
                elevation_angle_num = int(round(elevation_angle,2)/motor_degree)
    
                if azimuth_angle_update > the and elevation_angle_update > the:                                 #the (float(0))大於0
                    ser_motor.write((':P'+(str(int(azimuth_angle_num)))+','+(str(int(elevation_angle_num)))+',0,').encode())
                    time.sleep(float(abs(azimuth_angle_num - azimuth_angle_num_update)*0.0025/18))
                    time.sleep(float(abs(elevation_angle_num - elevation_angle_num_update)*0.0025/18))      
                
                elif azimuth_angle_update < the and elevation_angle_update > the:
                    ser_motor.write((':P'+(str(int(azimuth_angle_num)))+','+(str(int(elevation_angle_num)))+',0,').encode())
                    time.sleep(float(abs(azimuth_angle_num - azimuth_angle_num_update)*0.0025/18))
                    time.sleep(float(abs(elevation_angle_num - elevation_angle_num_update)*0.0025/18))
                    
                elif azimuth_angle_update > the and elevation_angle_update < the:
                    ser_motor.write((':P'+(str(int(azimuth_angle_num)))+','+(str(int(elevation_angle_num)))+',0,').encode())
                    time.sleep(float(abs(azimuth_angle_num - azimuth_angle_num_update)*0.0025/18))
                    time.sleep(float(abs(elevation_angle_num - elevation_angle_num_update)*0.0025/18))  
                    
                elif azimuth_angle_update < the and elevation_angle_update < the:   
                    time.sleep(0)    
      
                azimuth_angle_num_update = azimuth_angle_num
                elevation_angle_num_update = elevation_angle_num
                
    #                print('Distance %f, Position: x = %f, y = %f ,Alt = %f, azimuth_angle = %f ,elevation_angle = %f, azimuth_angle_num = %f, elevation_angle_num = %f, Datarate = %f, RSSI = %s, Distance = %s, tx-phy-rate = %s, tx-sector = %s '\
    #                      %(distance, e, -n, alt, azimuth_angle, elevation_angle, azimuth_angle_num, elevation_angle_num, Datarate.Datarate, ssh.Data_set[5], ssh.Data_set[9], ssh.Data_set[3], ssh.Data_set[6]))
    
                print('dis,e,n,u,rate:', distance, e, -n, alt, Datarate.Datarate, azimuth_angle, elevation_angle )
    
                End = time.time()
                data_time = End - Start
    
    #            publish.single(topic, np.round(Datarate.Datarate,2), qos=2, hostname=host)
    #            publish.single(topic_1, np.round(distance,2), qos=2, hostname=host)
    #            publish.single(topic_2, np.round(alt,2), qos=2, hostname=host)           
    #            msgs = [(topic,np.round(Datarate.Datarate,2), 2,  False), (topic_1, np.round(distance,2), 2, False), (topic_2, np.round(alt,2), 2, False)]
    #            publish.multiple(msgs, hostname=host)
                            
                with open(File_name +'.txt','at') as fout:
                    csvwriter = csv.writer(fout)
                    csvwriter.writerow([str(data_time),str(distance),str(Datarate.Datarate),str(elevation_angle),str(azimuth_angle),Lat_Lon_alt_Update[0],Lat_Lon_alt_Update[1],\
                                        Lat_Lon_alt_Update[2], str(alt),str(e[0]),str(-n[0]),str(u[0])])
                
    #            with open('example.txt','w+') as fout_plot:
    #                    csvwriter_plot = csv.writer(fout_plot)
    #                    csvwriter_plot.writerow([np.round(e[0],2), np.round(-n[0],2), np.round(data_time,2), Datarate.Datarate, np.round(elevation_angle,1), np.round(azimuth_angle,1)])        
    #                    csvwriter_plot.writerow([np.round(e[0],2), np.round(-n[0],2)])
    #                    print(np.round(e[0],2), np.round(-n[0],2))
    #            plt.gca().set_aspect('equal', adjustable='box')
    #            plt.pause(0.001)
            except IndexError:
                pass
    except KeyboardInterrupt:
        pass
    finally:
        Datarate.stop()
#        ssh.stop()
        GPS_port.stop()
        ser_motor.close()
        print('All serial close')

        
if __name__=='__main__':
    main()

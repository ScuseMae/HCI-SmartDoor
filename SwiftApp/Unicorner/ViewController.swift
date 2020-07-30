//  ViewController.swift
//  Created by Marcus Giarrusso on 4/22/18.

import UIKit
import CocoaMQTT

class ViewController: UIViewController, UIWebViewDelegate {
    // **** Set IP Address
    let mqttClient = CocoaMQTT(clientID: "iOS Device", host: "### IPAdress ###", port: 1883)
    
    // Button to connect to mqtt
    @IBAction func connectButton(_ sender: UIButton) {
        mqttClient.connect()
        print("Connected..")
    }
    
    // Button to disconnect from mqtt
    @IBAction func disconnectButton(_ sender: UIButton) {
        mqttClient.disconnect()
        print("Disconnected..")
    }
    
    // Ability to toggle gpio pin/led light on/off
    @IBAction func gpio40_Switch(_ sender: UISwitch) {
        if sender.isOn{
            mqttClient.publish("rpi/gpio", withString: "on")
            print("Switch_ON")
        }
        else{
            mqttClient.publish("rpi/gpio", withString: "off")
            print("Switch_OFF")
        }
    }
    
    @IBOutlet weak var webView: UIWebView!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = UIColor.darkGray
        // **** Set IP Address and port of your RasPi or local http stream ("http://xxx.xxx.x.xxx:xxxx")
        let stream_uri = "### Enter Stream_Url ###"
        
        // Delegate and Load
        webView.delegate = self
        webView.loadRequest(NSURLRequest(url: NSURL(string: stream_uri )! as URL) as URLRequest)
        
        // Change background color of webView or reduce size of webView in main.storyboard
        webView.backgroundColor = UIColor.clear
    }
    
    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
    }
    
}




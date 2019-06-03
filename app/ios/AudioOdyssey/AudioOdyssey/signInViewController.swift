//
//  signInViewController.swift
//  AudioOdyssey
//
//  Created by Kyle Maiorana on 5/24/19.
//  Copyright © 2019 SKAZ. All rights reserved.
//

import UIKit

class signInViewController: UIViewController {
    @IBOutlet weak var userNameTextField: UITextField!
    @IBOutlet weak var userPasswordTextField: UITextField!
    @IBOutlet weak var signInButton: UIButton!
    @IBOutlet weak var registerButton: UIButton!
    // Set the shouldAutorotate to False
    override open var shouldAutorotate: Bool {
        return false
    }
    
    // Specify the orientation.
    override open var supportedInterfaceOrientations: UIInterfaceOrientationMask {
        return .portrait
    }
    override func viewDidLoad() {
        super.viewDidLoad()
        registerButton.layer.cornerRadius = 10
        registerButton.clipsToBounds = true
        signInButton.layer.cornerRadius = 10
        signInButton.clipsToBounds = true
        // Do any additional setup after loading the view.
    }
    
    @IBAction func signInButtonTapped(_ sender: Any) {
        print("sign in button tapped")
        
    }
    
    @IBAction func registerNewAccountButtonTapped(_ sender: Any) {
        print("Register new account button tapped")
        
        let registerViewController = self.storyboard?.instantiateViewController(withIdentifier:
            "registerUserViewController") as! registerUserViewController
        
        self.present(registerViewController, animated: true)
        
    }
}

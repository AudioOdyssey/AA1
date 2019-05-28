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
    
    override func viewDidLoad() {
        super.viewDidLoad()

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
    /*
    // MARK: - Navigation

    // In a storyboard-based application, you will often want to do a little preparation before navigation
    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
        // Get the new view controller using segue.destination.
        // Pass the selected object to the new view controller.
    }
    */

}

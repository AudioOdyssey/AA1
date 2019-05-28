//
//  registerUserViewController.swift
//  AudioOdyssey
//
//  Created by Kyle Maiorana on 5/25/19.
//  Copyright © 2019 SKAZ. All rights reserved.
//

import UIKit

class registerUserViewController: UIViewController {
    @IBOutlet weak var firstNameTextField: UITextField!
    @IBOutlet weak var lastNameTextField: UITextField!
    @IBOutlet weak var emailAddressTextField: UITextField!
    @IBOutlet weak var passwordTextField: UITextField!
    @IBOutlet weak var repeatPasswordTextField: UITextField!
    
    override func viewDidLoad() {
        super.viewDidLoad()

        // Do any additional setup after loading the view.
    }
    @IBAction func cancelButtonTapped(_ sender: Any) {
        print("cancel button tapped")
        self.dismiss(animated: true, completion: nil)
    }
    @IBAction func signUpButtonTapped(_ sender: Any) {
        print("sign out button tapped")
        
        // validate required fields are filled
        if(firstNameTextField.text?.isEmpty)! || (lastNameTextField.text?.isEmpty)! || (emailAddressTextField.text?.isEmpty)! || (passwordTextField.text?.isEmpty)!
        {
            //display error message and return
            displayMessage(userMessage: "All Fields are Required")
            return
        }
        //validate passwords
        if((passwordTextField.text?.elementsEqual(repeatPasswordTextField.text!))! != true)
        {
            //display error message and return
             displayMessage(userMessage: "Passwords must match")
            return
        }
        //Create Activity Indicator
        let myActivityIndicator = UIActivityIndicatorView(style: UIActivityIndicatorView.Style.gray)
        
        // Position Activity Indicator in the center of the main view
        myActivityIndicator.center = view.center
        
        // If needed, you can prevent Acivity Indicator from hiding when stopAnimating() is called
        myActivityIndicator.hidesWhenStopped = false
        
        // Start Activity Indicator
        myActivityIndicator.startAnimating()
        
        view.addSubview(myActivityIndicator)
        
    }
    func displayMessage(userMessage:String) -> Void {
        DispatchQueue.main.async
            {
                let alertController = UIAlertController(title: "Alert", message: userMessage, preferredStyle: .alert)
                
                let OKAction = UIAlertAction(title: "OK", style: .default) { (action:UIAlertAction!) in
                    // Code in this block will trigger when OK button tapped.
                    print("Ok button tapped")
                    DispatchQueue.main.async
                        {
                            self.dismiss(animated: true, completion: nil)
                    }
                }
                alertController.addAction(OKAction)
                self.present(alertController, animated: true, completion:nil)
        }
    }
    

}

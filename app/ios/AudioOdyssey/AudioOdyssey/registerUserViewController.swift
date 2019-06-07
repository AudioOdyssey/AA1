//
//  registerUserViewController.swift
//  AudioOdyssey
//jj
//  Created by Kyle Maiorana on 5/25/19.
//  Copyright © 2019 SKAZ. All rights reserved.
//

import UIKit
import CountryPickerView

class registerUserViewController: UIViewController, UIPickerViewDelegate, UIPickerViewDataSource, UITextFieldDelegate, CountryPickerViewDelegate, CountryPickerViewDataSource{
    
    //Country Picker View functions
    func countryPickerView(_ countryPickerView: CountryPickerView, didSelectCountry country: Country) {}
    func preferredCountries(in countryPickerView: CountryPickerView) -> [Country]{
            var countries = [Country]()
            ["US", "CA","MX","JP"].forEach { code in
                if let country = countryPickerView.getCountryByCode(code) {
                    countries.append(country)
                }
            }
            return countries
        }
    
    func cellImageViewCornerRadius(in countryPickerView: CountryPickerView) -> CGFloat{
        return 1
    }
    func sectionTitleForPreferredCountries(in countryPickerView: CountryPickerView) -> String?{
        return "Active Countries"
    }
    
    func navigationTitle(in countryPickerView: CountryPickerView) -> String?{
        return "Choose a Country:"
    }
    
    //Outlet declarations
    
    @IBOutlet weak var cancelButton: UIButton!
    @IBOutlet weak var signUpButton: UIButton!
    @IBOutlet weak var firstNameTextField: UITextField!
    @IBOutlet weak var lastNameTextField: UITextField!
    @IBOutlet weak var emailAddressTextField: UITextField!
    @IBOutlet weak var passwordTextField: UITextField!
    @IBOutlet weak var repeatPasswordTextField: UITextField!
    @IBOutlet weak var scrollView: UIScrollView!
    @IBOutlet weak var picker: UIPickerView!
    @IBOutlet weak var datePicker: UIDatePicker!
    @IBOutlet weak var genderSegment: UISegmentedControl!
    @IBOutlet weak var lblDisplayDate: UILabel!
    @IBOutlet weak var usernameTextField: UITextField!
    @IBOutlet weak var countryPickerView: CountryPickerView!
    @IBAction func switchFlipped(_ sender: Any) {
       
    }
    @IBOutlet weak var disabilitySwitch: UISwitch!
    
    //Gender Selector
    @IBAction func genderChanged(_ sender: UISegmentedControl) {
        switch genderSegment.selectedSegmentIndex {
        case 0:
            print("first segement clicked")
        case 1:
            print("second segment clicked")
        case 2:
            print("third segemnet clicked")
        default:
            break;
        }  //Switch
    }
    //Date Picker
    @IBAction func datePicker(_ sender: Any) {
        // create a new instance of the NSDateFormatter
        let dateFormatter = DateFormatter()
        dateFormatter.dateStyle = .medium
        dateFormatter.timeStyle = .none
        let strDate = dateFormatter.string(from: datePicker.date)
        // Finally we set the text of the label to our new string with the date
        lblDisplayDate.text = strDate
    }
  
    

        //java.sql.Date sqlDate =java.sql.Date.valueOf(datepicker.getValue());

    //Country Picker View/Parse Country data
    var pickerData: [String] = [String]()
    var countries: [String] = {
        
        var arrayOfCountries: [String] = []
        
        for code in NSLocale.isoCountryCodes as [String] {
            let id = NSLocale.localeIdentifier(fromComponents: [NSLocale.Key.countryCode.rawValue: code])
            let name = NSLocale(localeIdentifier: "en").displayName(forKey: NSLocale.Key.identifier, value: id) ?? "Country not found for code: \(code)"
            arrayOfCountries.append(name)
        }
        
        return arrayOfCountries
    }()
    
    // Set the shouldAutorotate to False
    override open var shouldAutorotate: Bool {
        return false
    }
    // Locking the orientation.
    override open var supportedInterfaceOrientations: UIInterfaceOrientationMask {
        return .portrait
    }
    override func viewDidLoad() {
        super.viewDidLoad()
        //Scroll view sizing
            scrollView.contentSize = CGSize(width: self.view.frame.size.width, height: self.view.frame.size.height+390)
        //Delegations
            self.firstNameTextField.delegate = self
            self.lastNameTextField.delegate = self
            self.passwordTextField.delegate = self
            self.repeatPasswordTextField.delegate = self
            self.emailAddressTextField.delegate = self
            self.picker.delegate = self
            self.usernameTextField.delegate = self
            countryPickerView.delegate = self
        //Picker Data Sources
            self.picker.dataSource = self
            countryPickerView.dataSource = self
        //Button/Picker Formatting
        
            signUpButton.layer.cornerRadius = 6
            signUpButton.clipsToBounds = true
            cancelButton.layer.cornerRadius = 6
            cancelButton.clipsToBounds = true
            countryPickerView.showPhoneCodeInView = false
        //Language Data for Picker
            pickerData = ["English","Español","日本人"]
    }

    //Hide keyboard
    override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) {
        self.view.endEditing(true)
    }
    //Return key kills keyboard
    func textFieldShouldReturn(_ textField: UITextField) -> Bool {
        firstNameTextField.resignFirstResponder()
        lastNameTextField.resignFirstResponder()
        emailAddressTextField.resignFirstResponder()
        passwordTextField.resignFirstResponder()
        repeatPasswordTextField.resignFirstResponder()
        usernameTextField.resignFirstResponder()
        return (true)
    }
    //Language Picker Components and Counter
    func numberOfComponents(in pickerView: UIPickerView) -> Int {
        return 1
    }
    func pickerView(_ pickerView: UIPickerView, numberOfRowsInComponent component: Int) -> Int {
        if pickerView.tag == 1{
        return pickerData.count
        }
        else{
            return countries.count
        }
    }
    func pickerView(_ pickerView: UIPickerView, titleForRow row: Int, forComponent component: Int) -> String? {
        if pickerView.tag == 1{
            return pickerData[row]
        }else{
            return countries[row]
        }
    }
    
    //Button Functions
    @IBAction func cancelButtonBar(_ sender: Any) {
        print("cancel button tapped")
        self.dismiss(animated: true, completion: nil)
    }
    @IBAction func cancelButtonTapped(_ sender: Any) {
        print("cancel button tapped")
        self.dismiss(animated: true, completion: nil)
    }
    
    @IBAction func signUpButtonTapped(_ sender: Any) {
        print("sign up button tapped")
        
        // validate required fields are filled
        if(firstNameTextField.text?.isEmpty)! || (lastNameTextField.text?.isEmpty)! || (emailAddressTextField.text?.isEmpty)! || (passwordTextField.text?.isEmpty)! || (usernameTextField.text?.isEmpty)! || (genderSegment.selectedSegmentIndex == -1) || (lblDisplayDate.text?.isEmpty)! ||
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
        
        // Send HTTP Request to Register user
        let myUrl = URL(string: "http://3.216.9.206/app/user/new")
        var request = URLRequest(url:myUrl!)
        request.httpMethod = "POST"// Compose a query string
        request.addValue("application/json", forHTTPHeaderField: "content-type")
        request.addValue("application/json", forHTTPHeaderField: "Accept")
        
    //    let loginInfo = Login(usernameTextField.text!, passwordTextField.text!, genderSegment.selectedSegmentIndex, picker.selectedRow(inComponent: 0), countryPickerView!.selectedCountry.code, emailAddressTextField.text!, datePicker.date, firstNameTextField.text!, lastNameTextField.text!, disabilitySwitch.isOn)
        
        //Int to string conversion
        let genderString : Int = genderSegment.selectedSegmentIndex
        let myGender = String(genderString)
        let disabled: Bool = disabilitySwitch.isOn
        let myDisability = String(disabled)
        let lang : Int = picker.selectedRow(inComponent: 0)
        let langString = String(lang)
        print(myDisability)
        print(myGender)
        print(langString)
        let postString = ["first_name": firstNameTextField.text!,
                          "last_name": lastNameTextField.text!,
                          "email_address": emailAddressTextField.text!,
                          "password": passwordTextField.text!,
                          "username": usernameTextField.text!,
                          "date_of_birth": lblDisplayDate.text!,
                          "language_id": langString,
                          "country_of_origin":countryPickerView!.selectedCountry.code,
                          "gender": myGender,
                          "disabilities": myDisability
                          ] as [String: String]
  
        do {
            //try JSONSerialization.jsonObject(with: postString, options: [.allowFragments])
           request.httpBody = try JSONSerialization.data(withJSONObject: postString, options: .prettyPrinted)
            //try JSONSerialization.data(withJSONObject: postString, options: [.prettyPrinted])
        } catch let error {
            print(error.localizedDescription)
            displayMessage(userMessage: "Something went wrong. Try again.")
            return
        }
        
        let task = URLSession.shared.dataTask(with: request) { (data: Data?, response: URLResponse?, error: Error?) in
            
            self.removeActivityIndicator(activityIndicator: myActivityIndicator)
            
            if error != nil
            {
                self.displayMessage(userMessage: "Could not successfully perform this request. Please try again later")
                print("error=\(String(describing: error))")
                return
            }
            
            //Let's convert response sent from a server side code to a NSDictionary object:
            do {
                let json = try JSONSerialization.jsonObject(with: data!, options: .mutableContainers) as? NSDictionary
                
                if let parseJSON = json {
                    
                    
                    let userId = parseJSON["user_id"] as? String
                    print("User id: \(String(describing: userId!))")
                    
                    if (userId?.isEmpty)!
                    {
                        // Display an Alert dialog with a friendly error message
                        self.displayMessage(userMessage: "Could not successfully perform this request. Please try again later")
                        return
                    } else {
                        self.displayMessage(userMessage: "Successfully Registered a New Account. Please proceed to Sign in")
                    }
                    
                } else {
                    //Display an Alert dialog with a friendly error message
                    self.displayMessage(userMessage: "Could not successfully perform this request. Please try again later")
                }
            } catch {
                
                self.removeActivityIndicator(activityIndicator: myActivityIndicator)
                
                // Display an Alert dialog with a friendly error message
                self.displayMessage(userMessage: "Could not successfully perform this request. Please try again later")
                print(error)
        }
        }
        
        task.resume()
        
    }
    
    func removeActivityIndicator(activityIndicator: UIActivityIndicatorView)
    {
        DispatchQueue.main.async
            {
                activityIndicator.stopAnimating()
                activityIndicator.removeFromSuperview()
        }
    }
    
    func displayMessage(userMessage:String) -> Void {
        DispatchQueue.main.async
            {
                let alertController = UIAlertController(title: "Alert", message: userMessage, preferredStyle: .alert)
                
                let OKAction = UIAlertAction(title: "OK", style: .default) { (action:UIAlertAction!) in
                    // Code in this block will trigger when OK button tapped.
                    print("Ok button tapped")
                    //DispatchQueue.main.async
                     //   {
                      //      self.dismiss(animated: true, completion: nil)
                    //}
                }
                alertController.addAction(OKAction)
                self.present(alertController, animated: true, completion:nil)
        }
    }
}

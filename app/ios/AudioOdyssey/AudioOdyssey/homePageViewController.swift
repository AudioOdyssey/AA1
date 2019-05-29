//
//  homePageViewController.swift
//  AudioOdyssey
//
//  Created by Kyle Maiorana on 5/25/19.
//  Copyright © 2019 SKAZ. All rights reserved.
//

import UIKit

class homePageViewController: UIViewController {
    @IBOutlet weak var userFullNameLabel: UILabel!
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

        // Do any additional setup after loading the view.
    }
    @IBAction func signOutButtonTapped(_ sender: Any) {
        print("sign out button tapped")
    }
    @IBAction func loadMemberProfileButtonTapped(_ sender: Any) {
        print("load member button tapped")
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

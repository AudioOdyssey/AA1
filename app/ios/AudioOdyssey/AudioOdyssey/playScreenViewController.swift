//
//  playScreenViewController.swift
//  AudioOdyssey
//
//  Created by Adam Zhang on 6/5/19.
//  Copyright © 2019 SKAZ. All rights reserved.
//

import UIKit
import Speech


class playScreenViewController: UIViewController {
    
    let speechRecognizer = SFSpeechRecognizer()
    @IBOutlet weak var playButton: UIButton!
    
    @IBAction func saveButtonTapped(_ sender: Any) {
        //self.dismiss(animated: true, completion: nil)
    }
    @IBAction func playButtonTapped(_ sender: Any) {
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()

        // Do any additional setup after loading the view.
    }
    
    override public func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(true)
        
        //speechRecognizer!.delegate = self
        //This delegate needs to be added
        SFSpeechRecognizer.requestAuthorization { authStatus in //asks for permission to use speechRecog
            
            OperationQueue.main.addOperation {
                switch authStatus {
                    case .authorized: //if already given permission
                        self.playButton.isEnabled = true;
                    case .denied: //if user has denied permission
                        self.playButton.isEnabled = false;
                        self.playButton.setTitle("User denied access to speech recognition", for: .disabled)
                    case .restricted: //in the case the device doesn't allow speechRecog
                        self.playButton.isEnabled = false;
                        self.playButton.setTitle("Speech recognition is disabled on this device", for: .disabled)
                    case .notDetermined: //if has not yet been asked
                        self.playButton.isEnabled = false;
                        self.playButton.setTitle("Speech recognition not yet authorized", for: .disabled)
                @unknown default: //if functionality is added in future to authStatus
                    return
                }
            }
        }
    }
    
    func playGame() -> Int {
        return 0
    }

}

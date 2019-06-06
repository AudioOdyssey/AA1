//
//  Login.swift
//  AudioOdyssey
//
//  Created by Kyle Maiorana on 6/6/19.
//  Copyright © 2019 SKAZ. All rights reserved.
//

import Foundation

struct Login {
    var userId:Int
    var username:String
    var password:String
    var gender:Int
    var language:Int
    var countryOfOrigin:Int
    var email:String
    var dateOfBirth:Date
    var firstName:String
    var lastName:String
    var visionImpaired: Bool

    
    init (_ uId: Int, _ user: String, _ pass: String, _ gend: Int, _ lang: Int, _ countryO: Int,_ e: String, _ dob: Date, _ first: String, _ last: String, _ vision: Bool) {
        userId = uId
        username = user
        password = pass
        gender = gend
        language = lang
        countryOfOrigin = countryO
        email = e
        dateOfBirth = dob
        firstName = first
        lastName = last
        visionImpaired = vision
    }
}

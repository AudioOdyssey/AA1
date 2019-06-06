//
//  Location.swift
//  AudioOdyssey
//
//  Created by Kyle Maiorana on 6/5/19.
//  Copyright © 2019 SKAZ. All rights reserved.
//

import Foundation

struct Location {
    var storyId:Int
    var locationId:Int
    var locationName:String
    var originalDescription:String
    var shortDescription:String
    var postEventDescription:String
    var locationEventId:Int?
    var autoGoTo:Bool
    var nextLocId:Int?
    var locationVerified:Bool
    var locationVerificationStatus:Int
    var locationTimeStamp:Date?
    var verificationUserId:Int?
    
    init (_ sId: Int, _ locId: Int, _ locName: String, _ oDesc:String, _ sDesc: String, _ postDesc: String, _ locEventId: Int, _ autoGo: Bool, _ nextLoc: Int, _ locVer: Bool, _ locVerStat: Int, _ locTimeStamp: Date, _ verifUserId: Int) {
        storyId = sId
        locationId = locId
        locationName = locName
        originalDescription = oDesc
        shortDescription = sDesc
        postEventDescription = postDesc
        locationEventId = locEventId
        autoGoTo = autoGo
        nextLocId = nextLoc
        locationVerified = locVer
        locationVerificationStatus = locVerStat
        locationTimeStamp = locTimeStamp
        verificationUserId = verifUserId
    }
}

//
//  Object.swift
//  AudioOdyssey
//
//  Created by Kyle Maiorana on 6/5/19.
//  Copyright © 2019 SKAZ. All rights reserved.
//

import Foundation

struct Object {
    var storyId:Int
    var objectId:Int
    var objectStartingLocation:Int
    var objectName:String
    var objectDesc:String
    var canPickupObject:Bool
    var isHidden:Bool
    var unhideEventId:Int?
    
    init (_ sId: Int, _ oId: Int, _ oStartLoc: Int, _ oName:String, _ oDesc: String, _ canPickupO: Bool, _ isHid: Bool, _ unhideEId: Int) {
        storyId = sId
        objectId = oId
        objectStartingLocation = oStartLoc
        objectName = oName
        objectDesc = oDesc
        canPickupObject = canPickupO
        isHidden = isHid
        unhideEventId = unhideEId
    }
}

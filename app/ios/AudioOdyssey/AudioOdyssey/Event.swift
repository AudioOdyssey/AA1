//
//  Event.swift
//  AudioOdyssey
//
//  Created by Adam Zhang on 6/5/19.
//  Copyright © 2019 SKAZ. All rights reserved.
//

import Foundation

struct Event {
    var storyId:Int
    var eventId:Int
    var eventDesc:String
    var eventLocationId:Int
    var eventIsGlobal:Bool

    init (_ sId: Int, _ eId: Int, _ eDesc: String, _ eLocationId: Int, _ eIsGlobal: Bool) {
        storyId = sId
        eventId = eId
        eventDesc = eDesc
        eventLocationId = eLocationId
        eventIsGlobal = eIsGlobal
    }
    
    
}





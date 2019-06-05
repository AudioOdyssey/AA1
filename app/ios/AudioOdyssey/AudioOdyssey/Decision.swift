//
//  Decision.swift
//  AudioOdyssey
//
//  Created by Adam Zhang on 6/5/19.
//  Copyright © 2019 SKAZ. All rights reserved.
//

import Foundation

struct Decision {
    var storyId:Int
    var locationId:Int
    var sequenceNumber:Int
    var decisionId:Int
    var decisionName:String
    var isTransition:Bool
    var transitionLocationId:Int?
    var isHidden:Bool
    var isLocked:Bool
    var decisionDesc:String
    var showEventId:Int?
    var showObjectId:Int?
    var lockedEventId:Int?
    var unlockObjectId:Int?
    var lockedDesc:String?
    var aftermathDesc:String? //I assume only if not a transition
    var effectEventId:Int
    var causeEvent:Bool
    
    init (_ sId: Int, _ locId: Int, _ seqNum: Int, _ decId: Int, _ decName: String, _ isTrans: Bool,_ transLocId: Int, _ isHide: Bool, _ isLock: Bool, _ decDesc: String, _ showEvId: Int, _ showObjId:Int, _ lockEvId: Int, _ unlockObjId: Int, _ lockDesc: String, _ afterDesc: String, _ effectEvId: Int, _ causeEv: Bool) {
        storyId = sId
        locationId = locId
        sequenceNumber = seqNum
        decisionId = decId
        decisionName = decName
        isTransition = isTrans
        transitionLocationId = transLocId
        isHidden = isHide
        isLocked = isLock
        decisionDesc = decDesc
        showEventId = showEvId
        showObjectId = showObjId
        lockedEventId = lockEvId
        unlockObjectId = unlockObjId
        lockedDesc = lockDesc
        aftermathDesc = afterDesc
        effectEventId = effectEvId
        causeEvent = causeEv
    }
}

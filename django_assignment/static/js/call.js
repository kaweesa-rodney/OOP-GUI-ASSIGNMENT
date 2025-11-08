'use strict';

// Base URL for the application
const baseURL = "/"

// Get references to video elements from HTML
let localVideo = document.querySelector('#localVideo');  // Your own video
let remoteVideo = document.querySelector('#remoteVideo'); // Other person's video

// Variables to store information about the other user and their RTC message
let otherUser;
let remoteRTCMessage;

// Arrays and variables for managing the WebRTC connection
let iceCandidatesFromCaller = []; // Store ICE candidates if they arrive before connection
let peerConnection;  // The RTCPeerConnection object
let remoteStream;    // Stream from the remote user
let localStream;     // Your video/audio stream

let callInProgress = false;  // Track if a call is currently happening

// Function triggered when user clicks "Call" button
function call() {
    let userToCall = document.getElementById("callName").value;
    otherUser = userToCall;

    beReady()
        .then(bool => {
            processCall(userToCall)
        })
}

// Function triggered when user clicks "Answer" button
function answer() {
    beReady()
        .then(bool => {
            processAccept();
        })

    document.getElementById("answer").style.display = "none";
}

// Configuration for ICE servers (STUN/TURN servers for NAT traversal)
let pcConfig = {
    "iceServers": [
        { "url": "stun:stun.jap.bloggernepal.com:5349" },
        {
            "url": "turn:turn.jap.bloggernepal.com:5349",
            "username": "guest",
            "credential": "somepassword"
        },
        {"url": "stun:stun.l.google.com:19302"}
    ]
};

// SDP (Session Description Protocol) constraints for audio/video
let sdpConstraints = {
    offerToReceiveAudio: true,
    offerToReceiveVideo: true
};

// WebSocket connection setup
let socket;
let callSocket;
function connectSocket() {
    // Determine if we should use WSS (secure) or WS based on protocol
    let ws_scheme = window.location.protocol == "https:" ? "wss://" : "ws://";
    console.log(ws_scheme);

    // Create WebSocket connection
    callSocket = new WebSocket(
        ws_scheme
        + window.location.host
        + '/ws/call/'
    );

    // When socket connects, send login info
    callSocket.onopen = event =>{
        callSocket.send(JSON.stringify({
            type: 'login',
            data: {
                name: myName
            }
        }));
    }

    // Handle incoming WebSocket messages
    callSocket.onmessage = (e) =>{
        let response = JSON.parse(e.data);
        let type = response.type;

        // Handle different types of messages
        if(type == 'connection') {
            console.log(response.data.message)
        }
        if(type == 'call_received') {
            onNewCall(response.data)
        }
        if(type == 'call_answered') {
            onCallAnswered(response.data);
        }
        if(type == 'ICEcandidate') {
            onICECandidate(response.data);
        }
    }

    // Handler for receiving a new call
    const onNewCall = (data) =>{
        otherUser = data.caller;
        remoteRTCMessage = data.rtcMessage
        document.getElementById("callerName").innerHTML = otherUser;
        document.getElementById("call").style.display = "none";
        document.getElementById("answer").style.display = "block";
    }

    // Handler for when a call is answered
    const onCallAnswered = (data) =>{
        remoteRTCMessage = data.rtcMessage
        peerConnection.setRemoteDescription(new RTCSessionDescription(remoteRTCMessage));
        document.getElementById("calling").style.display = "none";
        console.log("Call Started. They Answered");
        callProgress()
    }

    // Handler for receiving ICE candidates
    const onICECandidate = (data) =>{
        console.log("GOT ICE candidate");
        let message = data.rtcMessage
        let candidate = new RTCIceCandidate({
            sdpMLineIndex: message.label,
            candidate: message.candidate
        });

        if (peerConnection) {
            console.log("ICE candidate Added");
            peerConnection.addIceCandidate(candidate);
        } else {
            console.log("ICE candidate Pushed");
            iceCandidatesFromCaller.push(candidate);
        }
    }
}

// Functions for sending different types of messages over WebSocket
function sendCall(data) {
    callSocket.send(JSON.stringify({
        type: 'call',
        data
    }));
    document.getElementById("call").style.display = "none";
    document.getElementById("otherUserNameCA").innerHTML = otherUser;
    document.getElementById("calling").style.display = "block";
}

function answerCall(data) {
    callSocket.send(JSON.stringify({
        type: 'answer_call',
        data
    }));
    callProgress();
}

function sendICEcandidate(data) {
    callSocket.send(JSON.stringify({
        type: 'ICEcandidate',
        data
    }));
}

// Get user's media stream and set up connection
function beReady() {
    return navigator.mediaDevices.getUserMedia({
        audio: true,
        video: true
    })
        .then(stream => {
            localStream = stream;
            localVideo.srcObject = stream;
            return createConnectionAndAddStream()
        })
        .catch(function (e) {
            alert('getUserMedia() error: ' + e.name);
        });
}

// Create RTCPeerConnection and add media stream
function createConnectionAndAddStream() {
    createPeerConnection();
    peerConnection.addStream(localStream);
    return true;
}

// Process outgoing call
function processCall(userName) {
    peerConnection.createOffer((sessionDescription) => {
        peerConnection.setLocalDescription(sessionDescription);
        sendCall({
            name: userName,
            rtcMessage: sessionDescription
        })
    }, (error) => {
        console.log("Error");
    });
}

// Process incoming call acceptance
function processAccept() {
    peerConnection.setRemoteDescription(new RTCSessionDescription(remoteRTCMessage));
    peerConnection.createAnswer((sessionDescription) => {
        peerConnection.setLocalDescription(sessionDescription);

        // Handle any queued ICE candidates
        if (iceCandidatesFromCaller.length > 0) {
            for (let i = 0; i < iceCandidatesFromCaller.length; i++) {
                let candidate = iceCandidatesFromCaller[i];
                try {
                    peerConnection.addIceCandidate(candidate).then(done => {
                        console.log(done);
                    }).catch(error => {
                        console.log(error);
                    })
                } catch (error) {
                    console.log(error);
                }
            }
            iceCandidatesFromCaller = [];
            console.log("ICE candidate queue cleared");
        } else {
            console.log("NO Ice candidate in queue");
        }

        answerCall({
            caller: otherUser,
            rtcMessage: sessionDescription
        })

    }, (error) => {
        console.log("Error");
    })
}

// Create new RTCPeerConnection
function createPeerConnection() {
    try {
        peerConnection = new RTCPeerConnection(pcConfig);
        peerConnection.onicecandidate = handleIceCandidate;
        peerConnection.onaddstream = handleRemoteStreamAdded;
        peerConnection.onremovestream = handleRemoteStreamRemoved;
        console.log('Created RTCPeerConnnection');
        return;
    } catch (e) {
        console.log('Failed to create PeerConnection, exception: ' + e.message);
        alert('Cannot create RTCPeerConnection object.');
        return;
    }
}

// Handle new ICE candidates
function handleIceCandidate(event) {
    if (event.candidate) {
        console.log("Local ICE candidate");
        sendICEcandidate({
            user: otherUser,
            rtcMessage: {
                label: event.candidate.sdpMLineIndex,
                id: event.candidate.sdpMid,
                candidate: event.candidate.candidate
            }
        })
    } else {
        console.log('End of candidates.');
    }
}

// Handle incoming remote stream
function handleRemoteStreamAdded(event) {
    console.log('Remote stream added.');
    remoteStream = event.stream;
    remoteVideo.srcObject = remoteStream;
}

// Handle removal of remote stream
function handleRemoteStreamRemoved(event) {
    console.log('Remote stream removed. Event: ', event);
    remoteVideo.srcObject = null;
    localVideo.srcObject = null;
}

// Clean up when window is closed
window.onbeforeunload = function () {
    if (callInProgress) {
        stop();
    }
};

// Stop the call and clean up resources
function stop() {
    localStream.getTracks().forEach(track => track.stop());
    callInProgress = false;
    peerConnection.close();
    peerConnection = null;
    document.getElementById("call").style.display = "block";
    document.getElementById("answer").style.display = "none";
    document.getElementById("inCall").style.display = "none";
    document.getElementById("calling").style.display = "none";
    document.getElementById("endVideoButton").style.display = "none"
    otherUser = null;
}

// Update UI when call is in progress
function callProgress() {
    document.getElementById("videos").style.display = "block";
    document.getElementById("otherUserNameC").innerHTML = otherUser;
    document.getElementById("inCall").style.display = "block";
    callInProgress = true;
}
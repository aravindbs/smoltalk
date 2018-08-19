var app = angular.module('smoltalk', []);

app.controller('chat', function ($scope, $http) {
    console.log("Init");

    var soc = io('/send');
    soc.on('connect', function (){
        console.log('Listeing to Server')
    });
    soc.on('to_event', function (data) {
        message = JSON.parse(data);
        console.log(message);
        if ((message.to_id == $scope.username) && (message.from_id == $scope.active_friend)) {
            $scope.messages.push(message);
            $scope.$apply();
            console.log($scope.messages);
        }
    });



    $scope.send_message = function (msg) {
        var socket = io('/recv');
        var new_message = { 'from_id': $scope.username, 'to_id': $scope.active_friend, 'body': msg };
        $scope.messages.push(new_message);
        socket.on('connect', function () {
            data = angular.toJson(new_message);
            socket.emit('from_event', data);
            $scope.message = null;
        });

    }

    $scope.load_user = function (user) {
        $scope.active_friend = user.username
        $http({
            method: 'GET',
            params: { 'from_id': user.username, 'to_id': $scope.username, 'no_of_msgs': 10 },
            url: $scope.base_url + 'api/messages',
            headers: {
             'Content-Type': 'application/json'
            }
        }).then(function (response) {
            $scope.messages = response.data;
        });
    }

});
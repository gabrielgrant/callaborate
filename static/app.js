//
// MayDay Volunteer Coordination Tool
//

if (typeof String.prototype.startsWith != 'function') {
  String.prototype.startsWith = function (str){
    return this.slice(0, str.length) == str;
  };
}

function CallerController($scope, $http) {
  $scope.showWelcome = true;
  $scope.state = 'landing.index'; // landing.signin, disconnected, connecting, connected.calling, connected.saving, connected.waiting
  $scope.id = {};
  $scope.callInfo = {};
  $scope.numCalls = 0;

  // Leaderboard
  var url = '/leaderboard'
  $http.get(url)
  .success(function(data, status, headers, config) {
      delete $scope.status;
      $scope.leaderBoard = data.leaderboard;
      $scope.totalCalled = data.total_called;
  }).error(function(data, status, headers, config) {
      $scope.status = status;
  });

  // ACTIONS

  $scope.signin = function(){
    $scope.state = 'disconnected';

    var url = '/sign_in'
    $http.post(url, $scope.id)
    .success(function(data, status, headers, config) {
        delete $scope.status;
        if(data.error === 'after_hours'){
          $scope.state = 'after_hours';
          return;
        }
    }).error(function(data, status, headers, config) {
        $scope.status = status;
    });
  };

  $scope.connect_caller = function(){
    $scope.state = 'connecting';

    var url = '/connect_caller'
    $http.post(url, $scope.id)
    .success(function(data, status, headers, config) {
        delete $scope.status;
        if(data.error === 'after_hours'){
          $scope.state = 'after_hours';
          return;
        }
        $scope.id.sessionId = data.sessionId;
    }).error(function(data, status, headers, config) {
        $scope.status = status;
    });
  
  };
  $scope.connect_callee = function(){
    $scope.state = 'connected.calling';
    
    var url = '/connect_callee'
    $http.post(url, $scope.id)
    .success(function(data, status, headers, config) {
        delete $scope.status;
        if(data.error === 'after_hours'){
          $scope.state = 'after_hours';
          return;
        }
        $scope.callee = data;
    }).error(function(data, status, headers, config) {
        $scope.status = status;
    });
  };
  $scope.save = function(){
    var url = '/save_call'
    var data = {
      caller: $scope.id,
      callee: $scope.callee,
      callInfo: $scope.callInfo
    };
    $http.post(url, data)
    .success(function(data, status, headers, config) {
        delete $scope.status;
        $scope.success = true;
        $scope.state = 'connected.hungup';
        $scope.callInfo = {};
        $scope.numCalls++;
    }).error(function(data, status, headers, config) {
        $scope.status = status;
    });
    $scope.status = 'saving';
  };
  
  $scope.saveStatus = function(status){
    $scope.callInfo.status = status;
    $scope.save();
  };
}

// vim: tabstop=8 expandtab shiftwidth=2 softtabstop=2

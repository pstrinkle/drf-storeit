(function () {
    'use strict';

    var StoreApp = angular.module('storeit_app', [
        'angularMoment',
        'ngAria',
        'ngCookies',
        'ngFilesizeFilter',
        'ngFileUpload',
        'ngResource',
        'ngSanitize',
        'ui.bootstrap',
        'ui.router',
    ]);

    StoreApp.directive('autolowercase', function() {
        return {
            require: 'ngModel',
            link: function(scope, element, attrs, modelCtrl) {
                modelCtrl.$parsers.push(function(input) {
                    return input ? input.toLowerCase() : "";
                });

                element.css("text-transform", "lowercase");
            }
        };
    });

    StoreApp.factory('Folders', ['$resource', '$rootScope', function ($resource, $rootScope) {
        return $resource($rootScope.restUrl + 'folder/:folderId', {}, {
            options: {method: 'OPTIONS', params: {format: 'json'}},
            update: {
                method: 'PUT',
                headers: {'Content-Type': 'application/json', 'Accept': 'application/json'}
            },
        });
    }]).factory('Images', ['$resource', '$rootScope', function ($resource, $rootScope) {
        return $resource($rootScope.restUrl + 'image/:imageId', {}, {
            options: {method: 'OPTIONS', params: {format: 'json'}},
            update: {
                method: 'PUT',
                headers: {'Content-Type': 'application/json', 'Accept': 'application/json'}
            },
        });
    }]).factory('Users', ['$resource', '$rootScope', function ($resource, $rootScope) {
        return $resource($rootScope.restUrl + 'user/:userId', {}, {
            options: {method: 'OPTIONS', params: {format: 'json'}},
            update: {
                method: 'PUT',
                headers: {'Content-Type': 'application/json', 'Accept': 'application/json'}
            },
        });
    }]);

    StoreApp.service('credentialsService', function ($rootScope, $http) {
        $rootScope.loggedIn = false;

        return {
            checkLogin: function(result) {
                $http({
                    url: '/auth/login/',
                    method: 'POST'
                }).then(function success(response) {
                    $rootScope.loggedIn = true;
                    result(true);
                }, function error(response) {
                    $rootScope.loggedIn = false;
                    result(false);
                });
            },
            setToken: function(token) {
                if (token) {
                    $rootScope.token = token;
                    localStorage.setItem('token', token);
                    $http.defaults.headers.common['Authorization'] = "Token " + token;

                    $rootScope.loggedIn = true;
                }
            },
            clearAuth: function() {
                delete $rootScope.token;
                localStorage.removeItem('token');
                delete $http.defaults.headers.common['Authorization'];

                delete $rootScope.user;
                localStorage.removeItem('user');

                $rootScope.loggedIn = false;
            },
            setUser: function(user) {
                if (user) {
                    $rootScope.user = user;
                    localStorage.setItem('user', JSON.stringify(user));
                }
            },
            getUser: function() {
                if ($rootScope.user) {
                    return $rootScope.user;
                }

                return null;
            },
        };
    });

    StoreApp.config(['$stateProvider', '$urlRouterProvider', '$httpProvider', function($stateProvider, $urlRouterProvider, $httpProvider) {

        $urlRouterProvider.otherwise('/');

        $stateProvider.state('main', {
            name: 'main',
            url: '/',
            templateUrl: 'partials/main.html',
            controller: 'indexCtrl',
        }).state('login', {
            name: 'login',
            url: '/login',
            templateUrl: 'partials/login.html',
            controller: 'loginCtrl',
        }).state('folder', {
            name: 'folder',
            url: '/folder/{folderId}',
            templateUrl: 'partials/folder.html',
            controller: 'folderCtrl',
        });

        /* XXX: Deal with this later.
        //http://stackoverflow.com/questions/23720003/angularjs-handling-401s-for-entire-app
        $httpProvider.interceptors.push(function($q) {
            return {
                'responseError': function(rejection) {
                    var defer = $q.defer();

                    if (rejection.status === 401) {
                        if (rejection.config.url === '/auth/login/') {
                            // you've gotten a 401 on the auth check.
                        } else {
                            console.dir(rejection);
                            $location.url('/login');
                        }
                    }

                    defer.reject(rejection);
                    return defer.promise;
                }
            };
        });
        */
    }]);

    /* App.run, lets you initialize global stuff. */
    StoreApp.run(function($rootScope, $state, credentialsService) {
        $rootScope.$on('$stateChangeError', console.log.bind(console));

        $rootScope.restUrl = '/api/v1/';

        credentialsService.setToken(localStorage.getItem('token'));
        credentialsService.setUser(JSON.parse(localStorage.getItem('user')));
    });

    StoreApp.controller('indexCtrl', ['$scope', 'credentialsService', function($scope, credentialsService) {
        $scope.currentlyLoggedIn = false;
        $scope.rootDir = 0;

        var loginStatus = function(state) {
            if (state) {
                $scope.currentlyLoggedIn = true;
                var user = credentialsService.getUser();
                $scope.rootDir = user.root;
            }
        };

        credentialsService.checkLogin(loginStatus);
    }]);

    StoreApp.controller('loginCtrl',
                        ['$scope', '$http', '$state', 'credentialsService', function($scope, $http, $state, credentialsService) {

        $scope.tryLogin = function() {
            var u = $scope.username;
            var p = $scope.password;

            function b64EncodeUnicode(str) {
                return btoa(encodeURIComponent(str).replace(/%([0-9A-F]{2})/g, function(match, p1) {
                    return String.fromCharCode('0x' + p1);
                }));
            }

            $http({
                url: '/auth/login/',
                method: 'POST',
                headers: {
                    'Authorization': 'Basic ' + b64EncodeUnicode(u + ':' + p)
                }
            }).then(function success(response) {
                console.log('Logged in!', new Date());
                console.log('response: ' + JSON.stringify(response, null, 2));

                credentialsService.setUser(response.data.user);
                credentialsService.setToken(response.data.token);

                $state.go('folder', {folderId: response.data.user.root});
            });
        };
    }]);

    StoreApp.controller('folderCtrl',
                        ['$scope', '$state', '$uibModal', '$cookies', 'credentialsService', 'Folders', 'Images', 'Upload',
                         function($scope, $state, $uibModal, $cookies, credentialsService, Folders, Images, Upload) {

        $scope.folder_name = '';
        $scope.folder = {};
        $scope.hasParent = false;
        $scope.layout = 'grid';

        if ($state.params.folderId) {
            /* good. */
            console.log('folderId: ' + $state.params.folderId);
        } else {
            /* no folder specified; send them to their root. */
            var user = credentialsService.getUser();
            $state.go('folder', {folderId: user.root});
            return;
        }

        function initialize() {
            var savedlayout = $cookies.get('layout');
            console.log('layout cookie value: ' + savedlayout);
            if (savedlayout) {
                /* just in case they've changed the value to be funny. */
                $scope.layout = (savedlayout === 'grid') ? 'grid' : 'table';
            }

            Folders.get({folderId: $state.params.folderId}).$promise
                .then(function(result) {
                    console.log('result: ' + JSON.stringify(result, null, 2));
                    $scope.folder_name = result.name;
                    angular.copy(result, $scope.folder);
                    $scope.folder.condensed = [];

                    if ($scope.folder.folder) {
                        $scope.hasParent = true;
                    }
                });
        }

        initialize();
        console.log('layout: ' + $scope.layout);

        $scope.loadNewFolder = function(event) {
            var modal = $uibModal.open({
                animation: true,
                ariaLabelledBy: 'modal-title-top',
                ariaDescribedBy: 'modal-body-top',
                templateUrl: 'partials/createfolder.html',
                size: 'sm',
                controller: 'createFolderCtrl',
                resolve: {
                    parentFolder: function() {
                        return $state.params.folderId;
                    },
                },
            });

            event.target.blur();

            modal.result.then(function success(result) {
                console.log('result: ' + JSON.stringify(result, null, 2));

                $scope.folder.folders.push({
                    name: result.name,
                    id: result.id,
                    updated: result.updated
                });
                // new folder created.
            }, function dismissed(result) {
                console.log('result: ' + result);
                console.log('modal dismissed.');
                // new folder canceled
            });
        };

        $scope.loadFolder = function(folderId) {
            $state.go('folder', {folderId: folderId});
        };

        $scope.parent = function() {
            $state.go('folder', {folderId: $scope.folder.folder});
        };

        $scope.uploadFiles = function(files) {
            $('#imageupload').blur();

            if (files && files.length) {
                for (var i = 0; i < files.length; i++) {
                    var f = files[i];

                    Upload.upload({
                        url: '/api/v1/image',
                        data: {
                            file: f,
                            name: f.name,
                            folder: $scope.folder.id,
                        }
                    }).then(function(resp) {
                        $scope.folder.images.push({
                            name: resp.data.name,
                            id: resp.data.id,
                            thumbnail: resp.data.thumbnail,
                            updated: resp.data.updated,
                            size: resp.data.size,
                        });
                    }, function(resp) {
                        console.log('Error status: ' + resp.status);
                    });
                }
            }
        };

        $scope.changeLayout = function() {
            /* simple toggle method for now. */
            $scope.layout = ($scope.layout === 'grid') ? 'table' : 'grid';
            $cookies.put('layout', $scope.layout);
        };

        $scope.condensed = function() {
            if ($scope.folder.condensed) {
                if ($scope.folder.condensed.length === $scope.folder.folders.length + $scope.folder.images.length) {
                    return $scope.folder.condensed;
                }

                $scope.folder.condensed.length = 0;
                for (var i = 0; i < $scope.folder.folders.length; i++) {
                    $scope.folder.condensed.push({
                        name: $scope.folder.folders[i].name,
                        id: $scope.folder.folders[i].id,
                        updated: $scope.folder.folders[i].updated,
                        type: 'folder',
                    });
                }

                for (var i = 0; i < $scope.folder.images.length; i++) {
                    $scope.folder.condensed.push({
                        name: $scope.folder.images[i].name,
                        id: $scope.folder.images[i].id,
                        updated: $scope.folder.images[i].updated,
                        size: $scope.folder.images[i].size,
                        type: 'image',
                    });
                }

                console.log('condensed size: ' + $scope.folder.condensed.length);
                return $scope.folder.condensed;
            }

            //angular.extend($scope.actions.data, data);
        };
    }]);

    StoreApp.controller('createFolderCtrl', ['$scope', '$uibModalInstance', 'Folders', 'parentFolder',
                                             function($scope, $uibModalInstance, Folders, parentFolder) {

        $scope.config = {};

        function initialize() {
            Folders.options().$promise
                .then(function(result) {
                    $scope.config = result.actions.POST;
                    $scope.config.name.pattern = new RegExp($scope.config.name.pattern);
                });
        }

        initialize();

        $scope.createFolder = function() {
            /* Try to create a new folder. */
            var newFolder = {
                folder: parentFolder,
                name: $scope.name,
            };

            Folders.save(newFolder).$promise
                .then(function(result) {
                    $uibModalInstance.close(result);
                });
        };

        $scope.cancel = function() {
            $uibModalInstance.dismiss('cancel');
        };
    }]);

})();

(function () {
    'use strict';

    // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String/endsWith
    if (!String.prototype.endsWith) {
        String.prototype.endsWith = function(searchString, position) {
            var subjectString = this.toString();
            if (typeof position !== 'number' || !isFinite(position) || Math.floor(position) !== position || position > subjectString.length) {
                position = subjectString.length;
            }
            position -= searchString.length;
            var lastIndex = subjectString.lastIndexOf(searchString, position);
            return lastIndex !== -1 && lastIndex === position;
        };
    }

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

    StoreApp.factory('Files', ['$resource', '$rootScope', function ($resource, $rootScope) {
        return $resource($rootScope.restUrl + 'file/:fileId', {}, {
            options: {method: 'OPTIONS', params: {format: 'json'}},
            update: {
                method: 'PUT',
                headers: {'Content-Type': 'application/json', 'Accept': 'application/json'}
            },
        });
    }]).factory('Folders', ['$resource', '$rootScope', function ($resource, $rootScope) {
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
                        ['$scope', '$state', '$uibModal', '$cookies', 'credentialsService', 'Files', 'Folders', 'Images', 'Upload',
                         function($scope, $state, $uibModal, $cookies, credentialsService, Files, Folders, Images, Upload) {

        $scope.folder_name = '';
        $scope.folder = {};
        $scope.hasParent = false;
        $scope.layout = 'grid';
        $scope.selected = {};
        /* interestingly, I can access this from the UI without it being attachd to the $scope... */
        var user = credentialsService.getUser();

        if ($state.params.folderId) {
            /* good. */
            console.log('folderId: ' + $state.params.folderId);
        } else {
            /* no folder specified; send them to their root. */
            $state.go('folder', {folderId: user.root});
            return;
        }

        var uploadStuff = function(files, type) {
            var url = '/api/v1/' + type;

            if (files && files.length) {
                for (var i = 0; i < files.length; i++) {
                    var f = files[i];

                    Upload.upload({
                        url: url,
                        data: {
                            file: f,
                            name: f.name,
                            folder: $scope.folder.id,
                        }
                    }).then(function(resp) {
                        var item = {
                            name: resp.data.name,
                            id: resp.data.id,
                            updated: resp.data.updated,
                            size: resp.data.size,
                        };

                        if (type === 'image') {
                            item['thumbnail'] = resp.data.thumbnail;
                            $scope.folder.images.push(item);
                        } else {
                            $scope.folder.files.push(item);
                        }
                    }, function(resp) {
                        console.log('Error status: ' + resp.status);
                    });
                }
            }
        };

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

        $scope.deselectAll = function(event) {
            event.target.blur();
            var items = Object.keys($scope.selected);
            for (var i = 0; i < items.length; i++) {
                delete $scope.selected[items[i]];
            }
            console.log('deselected all');
        };

        $scope.selectGrid = function(event, item, type) {
            event.stopPropagation();
            event.preventDefault();
            event.target.blur();

            // stopping this propogation doesn't work...
            var mashup = type + ',' + item.id;
            var nitem = {
                name: item.name,
                type: type,
                id: item.id,
            };

            console.log('mashup: ' + JSON.stringify(mashup, null, 2));

            if ($scope.selected[mashup]) {
                delete $scope.selected[mashup];
            } else {
                $scope.selected[mashup] = nitem;
            }
        };

        $scope.selectItem = function(event, item) {
            var mashup = item.type + ',' + item.id;
            var nitem = {
                name: item.name,
                type: item.type,
                id: item.id,
            };
            if ($scope.selected[mashup]) {
                delete $scope.selected[mashup];
            } else {
                $scope.selected[mashup] = nitem;
            }
        };

        $scope.filesToTrash = function(event) {
            event.target.blur();

            var toTrash = Object.keys($scope.selected);
            console.log('toTrash: ' + JSON.stringify(toTrash, null, 2));
            var files = [];
            var folders = [];
            var images = [];
            for (var i = 0; i < toTrash.length; i++) {
                var item = $scope.selected[toTrash[i]];
                var update = {
                    owner: user.id,
                    name: item.name,
                    folder: user.trash
                };

                if (item.type === 'file') {
                    Files.update({fileId: item.id}, update).$promise
                        .then(function(result) {
                            console.log('File deleted');

                            for (var j = 0; j < $scope.folder.files.length; j++) {
                                if ($scope.folder.files[j].id === item.id) {
                                    $scope.folder.files.splice(j, 1);
                                    break;
                                }
                            }
                        });
                } else if (item.type === 'folder') {
                    Folders.update({folderId: item.id}, update).$promise
                        .then(function(result) {
                            console.log('Folder deleted');

                             for (var j = 0; j < $scope.folder.folders.length; j++) {
                                if ($scope.folder.folders[j].id === item.id) {
                                    $scope.folder.folders.splice(j, 1);
                                    break;
                                }
                            }
                        });
                } else if (item.type === 'image') {
                    Images.update({imageId: item.id}, update).$promise
                        .then(function(result) {
                            console.log('Image deleted');

                             for (var j = 0; j < $scope.folder.images.length; j++) {
                                if ($scope.folder.images[j].id === item.id) {
                                    $scope.folder.images.splice(j, 1);
                                    break;
                                }
                            }
                        });
                }
            }
        };

        $scope.previewImage = function(event, image) {
            event.target.blur();
            event.stopPropagation();

            var modal = $uibModal.open({
                animation: true,
                ariaLabelledBy: 'modal-title-top',
                ariaDescribedBy: 'modal-body-top',
                templateUrl: 'partials/preview.html',
                size: 'lg',
                controller: 'previewImageCtrl',
                resolve: {
                    data: function() {
                        return image;
                    },
                },
            });

            modal.result.then(function success(result) {
                console.log('result: ' + JSON.stringify(result, null, 2));
            }, function dismissed(result) {
                console.log('result: ' + result);
                console.log('modal dismissed.');
            });
        };

        $scope.loadFolder = function(folderId) {
            $state.go('folder', {folderId: folderId});
        };

        $scope.parent = function() {
            $state.go('folder', {folderId: $scope.folder.folder});
        };

        $scope.uploadImages = function(files) {
            $('#imageupload').blur();
            uploadStuff(files, 'image');
        };

        $scope.uploadFiles = function(files) {
            $('#fileupload').blur();
            uploadStuff(files, 'file');
        };

        $scope.changeLayout = function() {
            /* simple toggle method for now. */
            $scope.layout = ($scope.layout === 'grid') ? 'table' : 'grid';
            $cookies.put('layout', $scope.layout);
        };

        $scope.fileType = function(name) {
            /* I should implement this file icon lookup as a  service or something. */

            // fa-file-video-o
            // fa-file-powerpoint-o
            // fa-file-audio-o
            // fa-file-excel-o
            // fa-file-text-o

            if (name.endsWith('.c') || name.endsWith('.py') || name.endsWith('.pl') || name.endsWith('.h')) {
                return 'fa-file-code-o';
            } else if (name.endsWith('.zip') || name.endsWith('.gz') || name.endsWith('.tgz') || name.endsWith('.bz2')) {
                return 'fa-file-archive-o';
            } else if (name.endsWith('.doc') || name.endsWith('.docx')) {
                return 'fa-file-word-o';
            } else if (name.endsWith('.pdf')) {
                return 'fa-file-pdf-o';
            } else {
                return 'fa-file-o';
            }
        };

        $scope.condensed = function() {
            if ($scope.folder.condensed) {
                var cnt = $scope.folder.folders.length + $scope.folder.images.length + $scope.folder.files.length;
                if ($scope.folder.condensed.length === cnt) {
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

                for (var i = 0; i < $scope.folder.files.length; i++) {
                    $scope.folder.condensed.push({
                        name: $scope.folder.files[i].name,
                        id: $scope.folder.files[i].id,
                        updated: $scope.folder.files[i].updated,
                        size: $scope.folder.files[i].size,
                        type: 'file',
                    });
                }

                console.log('condensed size: ' + $scope.folder.condensed.length);
                return $scope.folder.condensed;
            }

            //angular.extend($scope.actions.data, data);
        };
    }]);

    StoreApp.controller('previewImageCtrl', ['$scope', '$uibModalInstance', 'Images', 'data',
                                             function($scope, $uibModalInstance, Images, data) {
        $scope.image = {};

        Images.get({imageId: data.id}).$promise
            .then(function(result) {
                angular.copy(result, $scope.image);
                console.log('result: ' + JSON.stringify(result, null, 2));
            });
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

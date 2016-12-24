# drf-storeit

A basic image management application written with a UI written in AngularJS and a backend via django-rest-framework.  This is run via three docker containers: 1) one runs nginx, 2) runs the api, 3) runs a postgres instance.

Ultimately, this can be used within a home network running on something low-powered such as a raspberry pi, such that users within the same local network can readily share files via this or offload storage of files, either temporarily or permanently.  It doesn't presently tie into any backup system, but because you can place the mounts wherever you need; this can be easily achieved.

**This was designed without security in mind.**  The files are served directly via nginx and at present require no authentication to access.  If a user knows the full network path of the file, they can access it directly.  However, through the UI, a user can only see their own files and folders.

*This was simply implemented for fun*

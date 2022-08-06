# Eversports class booking

Script to book a specific class on a specific date, meant to run as a cron job.

## Credentials

Copy `credentials_template.json` to `credentials.json` and fill in the required information. The Eversports API is called using the mobile authentication mechanism. In order to get the information use e.g. the `Burp Suite` and capture some request. You should find the `deviceId` and a `Baerer Token` in the header.

* deviceId: You phones device id
* token: `Baerer Token` in the header
* facilityId: Id of the facility you want to go
* membershipId: Do a booking on your phone using the `Burp Suite` as proxy, you should get your membership id in one of the requests.

## Days

Enter the days (Monday: 1, ..Sunday: 7) into the array where you want to book a class. For other details, see the source code.

## Cron job

Run the job e.g. every day at 8am.

`0 8 * * * python3 <path/booking.py>`
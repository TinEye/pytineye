Changelog
=========

1.3
---
* Removed `total_results` from TinEyeResponse object since it's been moved to `stats`.
* Removed `contributor` attribute from Match object and replacing it with `tags` list.
* Added `stats` attribute to TinEyeResponse which is a dictionary containing statistics about
  the search.
* Added `score` and `domain` attributes to TinEyeResponse.
* Updated to use SHA256 to sign requests to the TinEye API.
* Switched to using urllib3[secure]

1.2
---
* Changing `remaining_searches` method to fit the new format.

1.1
---
* Added Python 3 support
* Replaced `simplejson` with `json`

1.0
---
* Added `total_results` to TinEyeResponse

0.1
---
* Initial release

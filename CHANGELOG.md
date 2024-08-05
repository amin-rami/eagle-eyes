# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),

## [Unreleased]
### Added
- adtrace log/metrics

## [2.11.0] - 2023-08-13
### Changed
- Update Behsa certificate

## [2.10.5] - 2023-08-06
### Added
- club intial app

## [2.10.4] - 2023-08-05
### Added
- top rank game-level base users API

## [2.10.3] - 2023-07-28
### Fixes
- eagleusers API call not sending data on post request

## [2.10.2] - 2023-07-26
### Added
- eagleusers API call logger

## [2.10.1] - 2023-07-26
### Added
- sentry for phone number and user_id methods

## [2.10.0] - 2023-07-26
### Fixed
- eaglue_users phone number and user_id methods

## [2.9.5] - 2023-07-25
### Changed
- docker base image
- package and library versions

## [2.9.4.hotfix1] - 2023-07-24
### Fixed
- allocate API

## [2.9.4] - 2023-07-16
### Added
- added Ad-ID to fully integrate with AdTrace 

## [2.9.3] - 2023-07-15
### Added
- loghandler for event processor
- do not process event if user_id is null

## [2.9.2] - 2023-07-12
### Added
- do not send mutual event if user_id/phone_number mapping does not exist

## [2.9.1] - 2023-07-12
### Added
- extra checking for cached reward token in allocation step

## [2.9.0] - 2023-07-12
### Fixed
- better tracing of reward allocation failure

## [2.8.2] - 2023-07-10
### Changed
- allocate API

## [2.8.1.hotfix2] - 2023-07-10
### Fixed
- proxy setting

## [2.8.1.hotfix1] - 2023-07-10
### Fixed
- adtrace event sending

## [2.8.1] - 2023-07-10
### Added
- general processor app
- engagement processor 
- adtrace API
### Changed
 - tests to match new user_id format

## [2.8.0] - 2023-07-08
### Fixed
- UUID validation

## [2.7.6.hotfix2] - 2023-06-25
### Fixed
- query with phone number in get_is_referee serializer method

## [2.7.6.hotfix1] - 2023-06-25
### Fixed
- get_is_referee serializer method

## [2.7.6] - 2023-06-25
### Removed
- referral_reward old models

## [2.7.5] - 2023-06-24
### Removed
- process event backward compatibility

## [2.7.4] - 2023-06-24
### Added
- added bw3 status code guard

## [2.7.3.hotfix2] - 2023-06-24
### Added
- process event backward compatibility

## [2.7.3.hotfix1] - 2023-06-24
### Fix
- add try except statement to phone_number service

## [2.7.3] - 2023-06-24
### Added
- referral submission backward compatibility

## [v2.7.2] - 2023-06-24
### Added
- old userid guard

## [v2.7.1] - 2023-06-23
### Added
- referral login route/view (orphan)
- user-id middleware
- userinfo APIs

### Changed
- bw3 profile API
- phonenumber -> userid
- referral specific models migrated from referral_reward

## [v2.7.0] - 2023-06-14
### Added
- separate error for unauthorized users

## [v2.6.4] - 2023-06-13
### Fixed
- content type for bw3

## [v2.6.3] - 2023-06-12
### Added
- bw3 allocation APIs

## [v2.6.2] - 2023-06-11
### Added
- container scan
- allocate active internet check
- authorization support to referral views

## [v2.6.1] - 2023-05-31
### Removed
- Removed reward token expiration timeout

## [v2.6.0] - 2023-05-30
### Added
- container scan
- allocate active internet check

## [v2.5.6] - 2023-05-27
### Added
- Added action group for OR operator in reward criterias
- Added sentry exception capturing in log middleware

## [v2.5.5] - 2023-05-20
### Added
- Added index to campaign models

## [v2.5.4] - 2023-05-20
### Added
- proxy to behsa sessions

## [v2.5.3] - 2023-05-17
### Changed
- Do not return a camapaign if the campaign type is not referee unless is the user is a referee

## [v2.5.2] - 2023-05-17
### Changed
- Campaign order based on last updated

## [v2.5.1] - 2023-05-17
### Added
- Added auth_number field for UserReward
### Removed
- Removed auth token owner validation

## [v2.5.0] - 2023-05-16
### Added
- Added claim date on validate view

## [v2.4.0.hotfix2] - 2023-05-15
### Change
- ignore user-id if headers present

## [v2.4.0.hotfix1] - 2023-05-15
### Fixed
- commit offset on ignoring non-game events

## [v2.4.0] - 2023-05-14
### Added
- Added sending separate events based on mutual actions
- Added return state of each reward for referral rewards
- Added campaign type and progress type fields for Campaign
- Added key for sending events for allowing pod increase
- Added calculating percentage based on progress type
- Added getting SSO from Authorization heeder 
### Changed
- Changed and refactored campaign state services

## [v2.3.2] - 2023-04-29
### Added
- Added referral reward for rewarding internet
- Added reward type field for campaigns
### Fixed
- Fixed one of behsa API's

## [v2.3.1] - 2023-04-19
### Changed
- Optimized processor
- Enhanced decrypting user id script

## [v1.26.5.hotfix4] - 2023-04-19
### Fixed
- CampiagnCheckpointSerializer image url field

## [v1.26.5.hotfix3] - 2023-04-19
### Changed
- Cache queries in inject_campaign_config function.

## [v1.26.5.hotfix2] - 2023-04-14
### Changed
- Do not Update user state in campaigns that has no chance.

## [v1.26.5.hotfix1] - 2023-04-03
### Changed
- Allow editing criteria of started stages.

## [v1.26.5] - 2023-03-29
### Added
- Added type definition to action parameters.

## [v1.26.4] - 2023-03-14
### Added
- Added request/response logger.

## [v1.26.3] - 2023-03-14
### Changed
- Allow string parameter values in events & count them in processor.

## [v1.26.2.hotfix2]
### Fixed
- max number of fields limit

## [v1.26.2.hotfix1] - 2023-03-12
### Added
- Added lottery_text and no_chance_image fields to campaign.

## [v1.26.2] - 2023-03-12
### Changed
- Process stages based on delay field (delay_days is deprecated).

## [v1.26.1] - 2023-03-12
### Added
- Added an env variable to determine old campaigns deprecation.
- Added Django Cacheops.
- Added campaign checkpoints.
- Added stage delay based on hour & minutes.
- Added campaign start_date, end_date and lottery_date to the CampaignStateList view.
### Changed
- Made campaign editable.
- Removed metadata from user state in campaigns and append them dynamically.
### Removed
- Removed campaign threshold field.

## [v1.26.0.hotfix2] - 2023-03-12
### Fixed
- headers cors

## [v1.26.0.hotfix1] - 2023-03-12
### Fixed
- Handled invalid game_id in game-processor.

## [v1.26.0] - 2023-03-9
### Change
- Return state of user in all started (finished or not finished) campaigns.

## [v1.25.3.hotfix2] - 2023-03-6
### Fixed
- Fixed problem with getting the user last stage.

## [v1.25.3.hotfix1] - 2023-03-5
### Fixed
- Fixed problem with bulk creating parsed event objects in campaign processor.

## [v1.25.3] - 2023-03-5
### Added
- Added the processor of game events.

## [v1.25.2.hotfix1] - 2023-03-4
### Added
- Check if the user can reach the campaign threshold.

## [v1.25.2] - 2023-02-24
### Added
- In EventList Endpoint, Read X-Token from header, decode it and set data to user_id.

## [v1.25.1] - 2023-02-23
### Added
- Added title to stages of campaign.

## [v1.25.0.hotfix2] - 2023-02-23
### Fixed
- Do not check soft-deleted stages in unique constraint.

## [v1.25.0.hotfix1] - 2023-02-23
### Fixed
- Fixed creating duplicate stages while assigning default stage to old RewardCriteria.

## [v1.25.0] - 2023-02-23
### Added
- Added Stages to support ordering and wait time between doing groups of criteria in campaigns.
- Added an image field to campaign to be viewed in UI.
- Added title (persian title) to RewardCriteria.
- Added metric for inserted events by action & vertical.
- Added a hyperlink field to each Criteria in order to redirect the user to it.
### Fixed
- Show user state for active campaigns that either has or has not state in them.

## [v1.24.2.hotfix1] - 2023-02-19
### Fixed
- Prevent deleting objects that are referenced in active campaigns, otherwise allow soft deleting them.

## [1.24.2] - 2023-02-19
### Fixed
- Reward criteria is uneditable after its campaign starts.
- Soft Delete LuckyWheel if it has been won by a user.

## [1.24.1] - 2023-02-14
### Added
- Added API endpoint to get status of user in all active campaigns.
### Fixed
- Fixed sending metrics about bulk inserted events in processor app.

## [1.24.0.hotfix1] - 2023-02-14
### Changed
- Process events in batch.
- Do not commit kafka offset if events batch are not processed successfully.
### Fixed
- Event processor app will be restarted if postgres connection is closed.

## [1.24.0] - 2023-02-08
### Added
- Added Gitlab CI, Dockerfile, gunicorn, etc.
- Added customized user model.
- Added jJWT authentication.
- Added EventList API endpoint to insert events.
- Added Campaign admin panel to define campaigns.
- Added the event stream processing program to calculate user state for each active campaign.
- Added CampaignStateDetails API endpoint to get user state in a given campaign.
- Added LuckyWheel app.
- Added LuckyWheel model and admin page.
- Added swagger API docs .

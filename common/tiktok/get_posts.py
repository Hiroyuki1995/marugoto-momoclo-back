from TikTokApi import TikTokApi

# Watch https://www.youtube.com/watch?v=-uCt1x8kINQ for a brief setup tutorial
verifyFp = "verify_l6ogcu9w_Ze1wiR4v_MKvs_4Ce6_B7jC_BacTqWLAjOyW"
# api = TikTokApi(custom_verifyFp=verifyFp, use_test_endpoints=True)
# results = 10
# hashtag = 'Messi'
# search_results = api.hashtag(name=hashtag)
# for tiktok in search_results:
#     print(tiktok['video']['playAddr'])

api = TikTokApi(custom_verify_fp=verifyFp, use_test_endpoints=True)
videos = api.search.search_type('takagireni', 'user')
print(type(videos))
print(videos)
print(videos.__next__())
# for video in videos:
#     print('video')

# if not using the "with" context manager approach, manually close:
api.shutdown()

# with TikTokApi(custom_verifyFp=verifyFp) as api:
#     #     for trending_video in api.trending.videos(count=50):
#     #         # Prints the author's username of the trending video.
#     #         print(trending_video.author.username)
#     print('A')
#     # for video in api.trending.videos():
#     results = api.search.videos('takagireni')
#     print(results)
#     # for video in api.search.videos('takagireni'):
#     #   # do something
#     #     print('B')
#     #     print(video)
#     #     user_stats = video.author.info_full['stats']
#     #     if user_stats['followerCount'] >= 10000:
#     #         print('test')
#     # maybe save the user in a database

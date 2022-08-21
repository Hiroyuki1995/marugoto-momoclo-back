import boto3


def insert_image_data():
    resource = boto3.resource('dynamodb')
    table = resource.Table('Photos')
    items = [
        {"person": "takagireni", "date": 20210819110428,
            "fileName": "2021-08-19_11-04-28-takagireni_official-GraphStoryImage-2643678606674257613.jpg"},
        {"person": "takagireni", "date": 20210819124321,
            "fileName": "2021-08-19_12-43-21-takagireni_official-GraphStoryImage-2643728379330156195.jpg"},
        {"person": "takagireni", "date": 20210820100653,
            "fileName": "2021-08-20_10-06-53-takagireni_official-GraphStoryImage-2644374414755335994.jpg"},
        {"person": "takagireni", "date": 20210820100925,
            "fileName": "2021-08-20_10-09-25-takagireni_official-GraphStoryImage-2644375682827648629.jpg"},
        {"person": "takagireni", "date": 20210820102158,
            "fileName": "2021-08-20_10-21-58-takagireni_official-GraphStoryImage-2644381996546833058.jpg"},
        {"person": "takagireni", "date": 20210820121425,
            "fileName": "2021-08-20_12-14-25-takagireni_official-GraphStoryImage-2644438596775153642.jpg"},
        {"person": "takagireni", "date": 20210821114116,
            "fileName": "2021-08-21_11-41-16-takagireni_official-GraphStoryImage-2645146713260343004.jpg"},
        {"person": "takagireni", "date": 20210822103744,
            "fileName": "2021-08-22_10-37-44-takagireni_official-GraphStoryImage-2645839480058950083.jpg"},
        {"person": "takagireni", "date": 20210822113953,
            "fileName": "2021-08-22_11-39-53-takagireni_official-GraphStoryImage-2645870779104616961.jpg"},
        {"person": "takagireni", "date": 20210822115339,
            "fileName": "2021-08-22_11-53-39-takagireni_official-GraphStoryImage-2645877703288155560.jpg"},
        {"person": "takagireni", "date": 20210822134705,
            "fileName": "2021-08-22_13-47-05-takagireni_official-GraphStoryImage-2645934792748423345.jpg"},
        {"person": "takagireni", "date": 20210823030437,
            "fileName": "2021-08-23_03-04-37-takagireni_official-GraphStoryImage-2646336189755263467.jpg"},
        {"person": "takagireni", "date": 20210823042336,
            "fileName": "2021-08-23_04-23-36-takagireni_official-GraphStoryVideo-2646375936514876134.jpg"},
        {"person": "takagireni", "date": 20210823042336,
            "fileName": "2021-08-23_04-23-36-takagireni_official-GraphStoryVideo-2646375936514876134.mp4"},
        {"person": "takagireni", "date": 20210824152530,
            "fileName": "2021-08-24_15-25-30-takagireni_official-GraphStoryImage-2647433895825815377.jpg"},
        {"person": "sasakiayaka", "date": 20210825034602,
            "fileName": "2021-08-25_03-46-02-ayaka_sasaki_official-GraphStoryImage-2647806584895081048.jpg"},
        {"person": "takagireni", "date": 20210825111258,
            "fileName": "2021-08-25_11-12-58-takagireni_official-GraphStoryImage-2648031546063024158.jpg"},
        {"person": "takagireni", "date": 20210825113321,
            "fileName": "2021-08-25_11-33-21-takagireni_official-GraphStoryImage-2648041812838424362.jpg"},
        {"person": "takagireni", "date": 20210825113322,
            "fileName": "2021-08-25_11-33-22-takagireni_official-GraphStoryImage-2648041816999311672.jpg"},
        {"person": "takagireni", "date": 20210825123041,
            "fileName": "2021-08-25_12-30-41-takagireni_official-GraphStoryImage-2648070659482386762.jpg"},
        {"person": "takagireni", "date": 20210825130123,
            "fileName": "2021-08-25_13-01-23-takagireni_official-GraphStoryImage-2648086112070204130.jpg"},
    ]

    for item in items:
        dict = table.put_item(Item=item)
        # print(dict)


if __name__ == '__main__':
    insert_image_data()

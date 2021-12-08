# MM-AVS: <u>M</u>ulti-<u>m</u>odal <u>A</u>rticle and <u>V</u>ideo <u>S</u>ummarization
A Full-Scale Dataset for Multi-modal Summarization


MM-AVS is a full-scale multimodal dataset comprehensively gathering documents, summaries, images, captions, videos, audios, transcripts, and titles in English from CNN and Daily Mail. To our best knowledge, this is the first collection that spans all modalities and nearly comprises all types of materials available in this community.


We're sharing them here for developers and researchers to explore, study, and learn from. 

## Preparation
Given the dataset is quite large, please download the demo firstly to make sure the dataset meets your requirement.

## Download
Download files include cnn.zip, dailymail.zip, train_id.txt and test_id.txt  
~~**Method1: FTP**  
ftp://45.77.122.178/pub/file_name (i.e., file_name->cnn.zip)~~  
**invalid: this server is not rented anymore in our lab**

~~**Method2: Baidu Yun**  
link：https://pan.baidu.com/s/1I7b18ddgvVvPmb3okaRzpQ   
password：uwbt~~  
**invalid: Baidu forbid**

**Method3: OneDrive**
link: https://mailnankaieducn-my.sharepoint.com/:f:/g/personal/fuxiyan_mail_nankai_edu_cn/Ep7NuWj9V9FLpI8weBt1O4oBw5sAHNSzaZptJSxmLa4g1g?e=6Ea3Po

Note: ~~Videos are always limited by network disk, we recommend to method1.~~

## Extension
The data scale is determined by its accompanied videos, considering this modality is more space-consuming than the other. The data acquirability code can be used for dataset extension.

## Citations

New papar is accepted as a short paper by NAACL2021.
```
@inproceedings{fu-etal-2021-mm,
    title = "{MM}-{AVS}: A Full-Scale Dataset for Multi-modal Summarization",
    author = "Fu, Xiyan  and
      Wang, Jun  and
      Yang, Zhenglu",
    booktitle = "Proceedings of the 2021 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies",
    month = jun,
    year = "2021",
    address = "Online",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2021.naacl-main.473",
    doi = "10.18653/v1/2021.naacl-main.473",
    pages = "5922--5926",
}
```

The original version can be found at ["Multi-modal Summarization for Video-containing Documents"](https://arxiv.org/abs/2009.08018).

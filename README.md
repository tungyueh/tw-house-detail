# Taiwan House Detail
## Install required packages
```bash
pip install -e .
```
Download chrome driver: https://chromedriver.chromium.org/getting-started

## Usage

* save html in folder named by region
```bash
house 591 save --region 新北五股區 --url https://market.591.com.tw/list\?regionId\=3\&sectionId\=48\&age\=_5,5_10,10_20\&purpose\=5\&sort\=3\&isSale\=1
```

* Show detail from folder named by region
```bash
house 591 show --region 新北五股區
```

* Generate md file to show photo of building
```bash
house 591 map --region 新北五股區
```

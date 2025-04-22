from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

app = FastAPI()

# CORS para dev/local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ajuste conforme o ambiente
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/scrape")
def scrape():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("window-size=1400,1800")

    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://www.confianca.com.br/")
        time.sleep(1.5)
        driver.find_element(By.XPATH, "//div[@class='box__button']").click()
        time.sleep(1)
        driver.find_element(By.XPATH, "//section/div/div/div/div/button").click()
        time.sleep(1)

        categorias = driver.find_elements(By.XPATH, "//div[@class='side-nav__menu-item']/a")
        lista_categoria = [c.get_attribute("href") for c in categorias]

        lista_prod = []
        lista_preco = []
        lista_cat = []
        lista_imagem = []

        for i in range(1, len(lista_categoria)):
            driver.get(lista_categoria[i])
            time.sleep(0.5)

            for _ in range(30):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

            products = driver.find_elements(By.CLASS_NAME, "product-shelf__name")
            precos = driver.find_elements(By.CLASS_NAME, "product-shelf__price-current")
            cat = driver.find_element(By.XPATH, "//div[2]/div/h2").text
            imagens = driver.find_elements(By.XPATH, "//section[2]/div/a/div/div/button/img")

            for idx, product in enumerate(products):
                lista_prod.append(product.text.strip())
                lista_cat.append(cat)
                lista_preco.append(precos[idx].text.strip() if idx < len(precos) else None)
                lista_imagem.append(imagens[idx].get_attribute("src") if idx < len(imagens) else None)

        results = []
        for i in range(len(lista_prod)):
            results.append({
                "produto": lista_prod[i],
                "preco": lista_preco[i],
                "categoria": lista_cat[i],
                "imagem": lista_imagem[i]
            })

        return {"results": results}

    finally:
        driver.quit()

from scrapers_dict import scrapers_

class ScraperMenager:
    def __init__(self):
        self.scrapers = [scraper() for scraper in scrapers_.values()]

    def get_recipes(self, *args, **kwargs):
        recipes = [scraper.get_recipes(*args, **kwargs) for scraper in self.scrapers]

        # temp
        count = 0
        for website in recipes:
            count += website["n_recipes"]
        print(f"Recipes - sum - {count}")

        return recipes

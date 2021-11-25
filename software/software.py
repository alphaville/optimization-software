import json


class BibTeX:
    __KEYS = ["type", "author", "title", "year"]

    def __init__(self, _dict=[]):
        self.__dict__.update(_dict)
        for key in BibTeX.__KEYS:
            if key not in self.__dict__.keys():
                self.__setattr__(key, None)

    def __author_str(self):
        if self.author is None:
            return ""
        if len(self.author) > 2:
            return f"{self.author[0]} et al."
        else:
            return " and ".join(self.author[0:2])

    def __repr__(self):
        return f"({self.type}) {self.__author_str()} ({self.year})"

    def __str__(self):
        sw_string = repr(self)
        for k in self.__dict__.keys():
            sw_string += f"\n  L {k}: {getattr(self, k)}"
        return sw_string


class Software:

    __KEYS = ["uid",  # unique ID (for referencing)
              "title",
              "software_type",  # from software type ontology
              "algorithm_type",  # from algorithms ontology
              "description",
              "license",  # from licences ontology
              "year",
              "institution",
              "url",
              "source",  # URL to source code (e.g., GitHub repo)
              "docs",  # URL to docs
              "author",  # list of authors
              "programming_language",  # list of programming languages
              "api",  # list of APIs (e.g., Python, MATLAB, etc)
              "logo",  # URL to logo
              "bib",  # BibTeX object or list thereof
              "version",  # latest version
              "dev_status",  # development status (alpha, beta, etc)
              "dependencies"  # list of dependencies (UIDs)
              ]

    def __init__(self, _dict=[]):
        self.__dict__.update(_dict)
        for key in Software.__KEYS:
            if key not in self.__dict__.keys():
                self.__setattr__(key, None)
            if key == "bib" and self.bib is not None:
                if isinstance(self.bib, list):
                    bib_list = self.bib
                    self.bib = []
                    for bib_item in bib_list:
                        self.bib += [BibTeX(bib_item)]
                else:
                    self.bib = BibTeX(self.bib)

    def __repr__(self):
        return f"<Software, uid: '{self.uid}', title: '{self.title}'>"

    def __attr_string(self, attr_name):
        if attr_name in Software.__KEYS:
            val = getattr(self, attr_name)
            if val is None:
                return ""
            if isinstance(val, list):
                if len(val) <= 2:
                    attr_string = f"\n L {attr_name}: {val}"
                else:
                    attr_string = f"\n L {attr_name}"
                    for v in val:
                        attr_string += f"\n     L {v}"
            else:
                attr_string = f"\n L {attr_name}: {val}"
            return attr_string
        else:
            return ""

    def __str__(self):
        sw_string = f"Software::{self.uid}"
        for k in Software.__KEYS:
            sw_string += self.__attr_string(k)
        return sw_string


class SwDiscoverer:

    def __init__(self, db_filename="data/database.json"):
        self.__db_filename = db_filename
        with open(db_filename) as fh:
            self.__data = json.load(fh)
        self.__all_sw = []
        for s_itm in self.__data["entries"]:
            self.__all_sw += [Software(s_itm)]
        self.__search_filters = []

    def get_by_id(self, uid):
        return list(filter(lambda x: x.uid == uid, self.__all_sw))

    def with_year(self, start=0, end=3000):
        def filter_year(z):
            return z.year is not None and start <= int(z.year) <= end

        self.__search_filters += [filter_year]
        return self

    def with_algorithm_type(self, algorithm_type):
        def filter_algorithm_type(z):
            return z.algorithm_type is not None and algorithm_type in z.algorithm_type

        self.__search_filters += [filter_algorithm_type]
        return self

    def find(self):
        all_sw = self.__all_sw

        def finder_filter(z):
            verdict = True
            for filt in self.__search_filters:
                verdict = verdict and filt(z)
            return verdict

        return tuple(filter(finder_filter, all_sw))


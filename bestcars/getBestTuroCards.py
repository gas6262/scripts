
cookie = "rr_u_cid=AKBzp7e7QnyytcUKbkbNyA; osano_consentmanager_uuid=73a1f112-ff01-4430-ab7c-1ce7e26f06d1; SPRING_SECURITY_REMEMBER_ME_COOKIE=M1NSQ2Q1bFdobDhnSnZxOGl2Ykludz09OkcvOEtxRi8vNklFN2RwSVhYZ3ZNZWc9PQ; _gtmeec=eyJlbSI6IjcwODlhOWQ4NWQzNzI5MWQ3MzNjNzQ2MzI4OWViOGNkZDcyMTA1ZTI5M2FkMTZiNGYyOTAxYzgxMTZiYTM2ODIiLCJjb3VudHJ5IjoiNzlhZGIyYTJmY2U1YzZiYTIxNWZlNWYyN2Y1MzJkNGU3ZWRiYWM0YjZhNWUwOWUxZWYzYTA4MDg0YTkwNDYyMSIsImV4dGVybmFsX2lkIjoiTVdFV2p4ZjZUaUtJMUNFQ2xoaHhYQSJ9; __stripe_mid=25dccdb2-3ffe-4f7f-bab9-57e90b405fb3390140; osano_consentmanager=Vwtu72ZLF5WBIwMrfcuaeOMUAam4mSWH_XB4lPv-d-_5WK6xp3vcks--5KSE7udG1EokyCvqH8fEz_hLJRFH1kP3qpJXLkJEYDSi4ueXbzphtDkqVQQxTo3zA2-1G-50cD3il_7FtsTAFVDzueD8YeynvF3Wph64uDBb25NNtnjku0cPbib-8RbTJ7XWNPZpF0qhr5_3Vlzjmxx5bc1hPwkfhpm6BSoueX_sdHTYVS6UCRE-0mos-2QbJNhzYDmh-3uK8xy354gSsKDVuCVVWwtHRwKmXgBFzTIUzByMibeWrI7pDQyPHyToWcqkiXkCN5_A7WwBgHc=; FPAU=1.1.1181458470.1755695806; __cf_bm=EEqS2r5odhmaNbiXRT_KjFk.RK5Wt0b0j8nZ5i3DS2M-1759698598-1.0.1.1-Gl0Rupb2sY1IZrxgxYnHexldwE3wCaWC0YhBmKWGg9kvy_egAbX5P514NIdAFO6Xte67ys3rYlhWHxNO.vRtTkiq3k9AfN_nMMl08tSB8LBqUnk160oNoDW52GXUR1fz; _cfuvid=oB0Xn2KRPfJJPeCRQ3X.nQ.KBaPInOOy6fKk7fSIHlg-1759698598157-0.0.1.1-604800000; sid=Zr971c9gSGy5HZyReX1wSA; JSESSIONID=428e40f2-d8d2-43e5-862f-a0bd90653841; cf_clearance=DPM.jwrspUhFnj_MdwfduqyDyNdKnbdg4X87HBv1A7M-1759698598-1.2.1.1-OrNaLGvH16eCWLfxsZSJsicEBCymCVsfonWv4gee1ueGVRdIhqUl0gC57_gR5TiDlLDNsTiGCyGkoUAJtElWBoUiYEPqZrKz4_nw8shr29Duic0x.Uf2IoUulCt8eZ8kN_EQX5hDGrX_Zu8Df20f8EgatEEJ5s8IOjPxjaIn5bbtLhHbr0ObzIoqbzYjPEYbshU0VbRaycxFWUrE17t6e1.0gCqbwhL_yMPgusmCwiA; _gcl_au=1.1.97822129.1759698599; ajs_user_id=MWEWjxf6TiKI1CEClhhxXA; ajs_anonymous_id=768f794a-f8e3-4687-9b61-d1499696e32a; _ga=GA1.1.2592255.1759698600; _uetsid=a924d2f0a22f11f091c58b4eb3ee7adb; _uetvid=b94a7600d35d11efb3cfc3bb3c49a161; _clck=ixpr8d%5E2%5Efzw%5E0%5E2104; _clsk=1119b30%5E1759698604251%5E1%5E1%5Ea.clarity.ms%2Fcollect; times={%22endDate%22:%2210/10/2025%22%2C%22endTime%22:%2210:00%22%2C%22flexibleType%22:%22NOT_FLEXIBLE%22%2C%22monthlyEndDate%22:%2201/19/2026%22%2C%22monthlyStartDate%22:%2210/19/2025%22%2C%22searchDurationType%22:%22DAILY%22%2C%22startDate%22:%2210/07/2025%22%2C%22startTime%22:%2210:00%22}; preferredLocale=en-US; _ga_92NQ4TK3Z9=GS2.1.s1759698599$o1$g1$t1759698623$j36$l1$h1114821957"
query = {"filters":{"engines":[],"features":[],"location":{"country":"US","type":"area","point":{"lat":27.7671271,"lng":-82.6384451}},"makes":[],"models":[],"tmvTiers":[],"types":[]},"flexibleType":"NOT_FLEXIBLE","searchDurationType":"DAILY","sorts":{"direction":"ASC","type":"RELEVANCE"}}
url = "https://turo.com/api/v2/search"

def get_json(url, cookie=None):
    import requests
    headers = {"Cookie": cookie} if cookie else {}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def post_json(url, data=None, cookie=None):
    import requests
    headers = {"Cookie": cookie} if cookie else {}
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    return response.json()

resp = post_json(url, data=query, cookie=cookie)
print(resp)

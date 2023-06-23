import os
import sys
import time
import argparse


def main(directory):
    print(f"Renaming files in {directory}")
    name_dict = {}

    # Tiktok to Instagram
    # name_dict["tiktok"] = "instagram"

    name_dict['janechuen_๘'] = "jane.chuenn_๘"
    name_dict['jomkanit_๘'] = "jomkanitha_๘"
    name_dict['aeluckvarin_๘'] = "ae_luckvarin_๘"
    name_dict['nickylityy_๘'] = "nickylity_๘"
    name_dict['mewsutthiiii_๘'] = "mewsutthi_๘"
    name_dict['naranphatphat_๘'] = "anannaranphat_๘"
    name_dict['mean.meannaem_๘'] = "mean.minnie_๘"
    name_dict['fewop__๘'] = "fewxxy_fewop__๘"

    name_dict['balloonpinsuda_๘'] = "balloon_balloon_๘"
    name_dict['giftbenjasiriwan_๘'] = "sichanart_๘"

    name_dict['nokkabukistyle_๘'] = 'nokkabuki_๘'
    name_dict['lanlacha_๘'] = "happylanchan_๘"
    name_dict['lanhimayani_๘'] = "happylanchan_๘"
    name_dict['aumnch_๘'] = "aumnch__๘"
    name_dict['apaly__๘'] = "apaly_๘"
    name_dict['nuchnichhh_๘'] = "nuchnichh_๘"
    name_dict['ms.lannalin_๘'] = "lannalinn_๘"
    name_dict['phanthikawong_๘'] = "ammu.wong_๘"
    name_dict["bbaiiporrr_๘"] = "bnt.p_๘"
    name_dict["bumibuta_๘"] = "bumi_buta_๘"
    name_dict["j.supapon_๘"] = "jangggg_๘"
    name_dict["kawaleereview_๘"] = "k.awalee_๘"
    name_dict["boattie_๘"] = "mooboatt_๘"
    name_dict["natthaphg_๘"] = "nattha.phg_๘"

    # IG change username
    # name_dict['piaaaaanooooo'] = "babyxpiano"
    # name_dict["jennifer__j"] = "jennifer.jingg"
    # name_dict["docsmile.dogseason"] = "docsmile_mild_mind_my"
    # name_dict["fai_prawploi"] = "faiprawploi"

    
    for old_name, new_name in name_dict.items():
        print(f"{old_name}, {new_name}")
        old_name = old_name + "_"
        new_name = new_name + "_"
        time.sleep(1)
        print("-----------------------Start of Old Name ----------------------")
        for file in os.listdir(directory):
            if (file.startswith(old_name)):
                print(file)
                os.rename(file, file.replace(old_name, new_name))
        print("-----------------------End of Old Name ----------------------")
        time.sleep(1)
        print("-----------------------Start of New Name ----------------------")
        for file in os.listdir(directory):
            if (file.startswith(new_name)):
                print(file)
        print("-----------------------End of New Name ----------------------")
        time.sleep(1)

        print("----------------------- Start of .jpeg ----------------------")
        for file in os.listdir(directory):
            if (file.endswith(".jpeg")):
                print(file)
                os.rename(file, file.replace(".jpeg", ".jpg"))
        print("----------------------- End of .jpeg ----------------------")
        print("-----------------------Start of .jpeg ----------------------")
        for file in os.listdir(directory):
            if (file.endswith(".jpeg")):
                print(file)
        print("----------------------- End of .jpeg  ----------------------")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process directory argument')
    parser.add_argument('-d', '--directory', type=str,
                        default='./', help='Directory path')
    args = parser.parse_args()
    main(args.directory)

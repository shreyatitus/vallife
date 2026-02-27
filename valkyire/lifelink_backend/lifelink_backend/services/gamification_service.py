def assign_points(donor):
    donor.points += 10

    if donor.points >= 50:
        return "Gold Donor Badge"
    elif donor.points >= 20:
        return "Silver Donor Badge"
    else:
        return "Bronze Donor Badge"
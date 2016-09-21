"""Helper script for managing teams."""

import sys

import models


def check_teams():
	print("Checking for existing teams...\n")

	teams = models.Team.get_teams()
	ids = []

	print("Listing team names:")

	for team in teams:
		print("Team {}: {}".format(team.id, team.name))
		ids.append(team.id)

	print("If you would like further team details, enter the team ID.")
	print("If you would like to delete an existing team, enter DELETE followed by the team ID.")
	print("Hitting ENTER will exit the program.")
	print("Example: DELETE 4")

	response = input(">>> ").strip()

	if len(response) > 0 and response.split()[0] == "DELETE":
		# User wants to delete a team
		try:
			team_id = int(response.split()[1])
			delete_team(team_id)
		except ValueError:
			print("[!] Invalid response!")
			sys.exit(1)
	elif len(response) > 0:
		# User wants team details
		try:
			team_id = int(response)
			if team_id in ids:
				print("Getting team details...\n")
				team_detail(team_id)
			else:
				print("Team with that ID does not exist.")
		except ValueError:
			print("[!] Invalid response!")
			sys.exit(1)


def create_team():
	print("Please supply the details of the new team...\n")
	
	name = input("Team name: ")
	institution = input("Institution: ")
	code = input("Code: ")

	print("\nAttempting to create new team...")
	try:
		models.Team.create_team(
			name=name,
			institution=institution,
			code=code
		)
		print("[!] Team created successfully!")
		print("Please remember the code {} for team {}".format(code, name))
	except ValueError as e:
		print("[!] Team creation failed! Error: {}".format(e))


def delete_team(team_id):
	"""Offer ability to delete team with given ID."""
	team_detail(team_id)
	check = input("Are you sure you would like to delete this team? [N/y] ")
	if check.upper() == "Y":
		print("Deleting team...")
		models.Team.delete_team(team_id)
		print("[!] Team deleted!")
	else:
		print("Canceling... no action taken.")


def team_detail(team_id):
	"""Supply team details given it's ID."""
	team = models.Team.get_team(team_id)
	print("Team name:", team.name)
	print("Institution:", team.institution)
	print("Team code:", team.code)


def main():
	print("[#] Team Manager [#]\n")
	task = input("Would you like to check existing teams or create a new one? [CHECK/create] ")
	if task.upper() == "CREATE":
		create_team()
	else:
		check_teams()


if __name__ == '__main__':
	main()
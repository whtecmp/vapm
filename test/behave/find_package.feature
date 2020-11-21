Feature: find-package
	Scenario: Find package
		Given an English speaking user
		When the user says "find package 2to3"
		Then "vapm" should replay with "Got 6 results, including a full match"


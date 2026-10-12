#For PR #57:
As part of requirement [ “verify the player is on campus before allowing gameplay”], the player needs to tap Play, have their device location sent to the system, and be either allowed to start (on campus) or blocked with a message (off campus). Therefore, I implemented code so that the game can ask the system whether a set of coordinates is on campus, for all players and for the game feature that will call it later. 

When I reviewed the service, repository and router for this functionality, I noticed that verify_location fetched the boundary itself from the repository and had no way to receive a database session. It also used a cache that would serve stale data once the boundary lives in a database. That would force changes to the service when the database arrives. Therefore, I changed verify_location to take the boundary rings as a parameter, and the router now gets them through Depends(get_campus_polygons). Only location_repo.py has to change for the database switch, and comments in that file list the steps.

When I tested the endpoint manually in FastAPI /docs with an off-campus coordinate, I got a 500 error. The cause was that I had moved the boundary file from data/ to temp/ without updating the path in location_repo.py. Therefore, I updated _BOUNDARY_FILE to the new folder, and the same request returned allowed: false with the message.

When CI ran on the PR, it failed with ModuleNotFoundError: No module named 'src'. My pytest.ini had pythonpath = src, which only works for imports without the src. prefix, and I had only ever run python -m pytest locally, which adds the repo root automatically. Therefore, I changed it to pythonpath = . src. I confirmed that plain pytest passes locally, matching how CI runs it.

The PR contains one deliberate temporary element: the campus boundary is read from temp/campus_boundary.geojson because the database doesn’t exist yet. It is not a workaround in the logic. The check itself is a complete implementation, and the file is isolated behind get_campus_polygons() in location_repo.py. When the database arrives, only the body of that function changes and the GeoJSON is deleted or kept as seed data.

The PR only contains small functions that are 1 to 11 lines long. The longest is point_in_ring at 11 lines, and the others are 1, 2, 3, and 9 lines.

I did [read through each function and searched for repeated values and unused imports] to ensure my contribution does not contain any of the following:
-hardcoded values (the messages and boundary path are named constants)
-duplicate code
-dead code
-unnecessary function calls
-excessive conditional logic
-deep nesting
-high cyclomatic complexity
-classes/modules/functions with many unrelated responsibilities

The review by ian suggested that using a polygon for the boundary is not going to follow our goal of making the system maintainable without editing the code. So i changed from polygons to a centerpoint with a set radius.

This work is written in location_service.py, location_repo.py, location_schema.py and location_router.py because the project’s layered structure separates services (logic), repositories (data access), schemas (validation) and routers (HTTP). This keeps the check reusable by the game feature and the database change isolated.

This work belongs in process “Verify location” in the DFD because it decides allowed/blocked from a coordinate, and the boundary lookup in location_repo.py corresponds to the read from the campus boundary store.

#Testing receipts PR# 57:
The functionality works correctly because the happy path tests test_on_campus_allows_start and test_endpoint_on_campuspassed.

I wrote tests to cover abnormal situations involving no boundary data (test_no_boundary_data_blocks) and invalid coordinates (test_endpoint_rejects_invalid_coordinates, which returns a 422), and they passed.

I checked that these negative cases involving off-campus coordinates (test_off_campus_blocks_start_with_message, run for downtown Kelowna, Vancouver, (0, 0) and a point just north of the boundary, and test_endpoint_off_campus) were blocked with the message, as expected.

When I reviewed the first version of the tests, I noticed they depended on the real placeholder campus boundary. They would break if the boundary changed or when the database arrived. Therefore, I changed them to use a small fake campus passed into the service, and to override the boundary dependency for endpoint tests.

Among these tests, test_on_campus_allows_start, test_off_campus_blocks_start_with_message, test_no_boundary_data_blocks and test_file_boundary_loads_and_contains_a_ring are unit tests, and test_endpoint_on_campus, test_endpoint_off_campus and test_endpoint_rejects_invalid_coordinates are integration tests, because they exercise the router, schema validation and service together through TestClient.

These tests are included in the directory tests/test_location_service.py.
This new test PR did not break anything else in the system because I ran the full suite with pytest, and all 11 tests passed, including the existing test_tests.py. 


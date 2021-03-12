test-push:
	act -P ubuntu-latest=nektos/act-environments-ubuntu:18.04
test-schedule:
	act schedule -P ubuntu-latest=nektos/act-environments-ubuntu:18.04

clean:
	rm database/metadata.db*
	rm database/all_identifications.tsv
	rm database/all_sampleinformation.tsv
	rm temp/component_matrix.csv
	rm temp/eigs_var.csv
	rm temp/original_pca.csv
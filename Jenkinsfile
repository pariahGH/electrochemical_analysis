pipeline {
     agent {
		docker {
			image 'cdrx/pyinstaller-windows:python3' 
		}
	}
    stages {
		stage ('Prep'){
			steps{
				checkout(
					[$class: 'GitSCM', branches: [[name: "origin/master"]]]
				)
			}
		}
		stage ('Build - Lab Screen Recorder') {
            when {
                expression {
					//only build if there have been changes
					recorderChanges = sh('git diff origin/master^ origin/master^^ lab_screen_recorder')
					return recorderChanges != null
				}
            }
            steps {
                sh 'pyinstaller --onefile lab_screen_recorder/lab_screen_recorder_gui.py' 
            }
            post {
                success {
                    archiveArtifacts 'dist/lab_screen_recorder_gui.exe' 
                }
            }
        }
		stage ('Build - Lab Data Analysis') {
            when {
                expression {
					//only build if there have been changes
					dataAnalysisChanges = sh('git diff origin/master^ origin/master^^ lab_data_analysis')
					return dataAnalysisChanges != null
				}
            }
            steps {
                sh 'pyinstaller --onefile lab_data_analysis/data_analysis_gui.py' 
            }
            post {
                success {
                    archiveArtifacts 'dist/data_analysis_gui.exe' 
                }
            }
        }
		stage ('Build - Fuel Cell Power Model') {
            when {
                expression {
					//only build if there have been changes
					fuel_cell_power_model = sh('git diff origin/master^ origin/master^^ fuel_cell_power_model')
					return fuel_cell_power_model != null
				}
            }
            steps {
                sh 'pyinstaller --onefile fuel_cell_power_model/main.py -n fuel_cell_power_model.exe' 
            }
            post {
                success {
                    archiveArtifacts 'dist/fuel_cell_power_model.exe' 
                }
            }
        }
        stage('End'){
			steps{
				script{
					if(recorderChanges == null){
							echo 'No changes to lab_screen_recorder - build did not run'
					}
					if(dataAnalysisChanges == null){
							echo 'No changes to lab_data_analysis - build did not run'
					}
					if(fuel_cell_power_model == null){
							echo 'No changes to Fuel Cell Power Model - build did not run'
					}
				}
			}
        }
	}
}
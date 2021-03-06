# import basic libarires
import pandas as pd
import numpy as np

import warnings
warnings.filterwarnings("ignore")

# prep methods
from sklearn.model_selection import train_test_split

# Scaler
from sklearn.preprocessing import MinMaxScaler

# Feature Engineering methods
from sklearn.linear_model import LinearRegression
from sklearn.feature_selection import SelectKBest, f_regression, RFE



# Classification Modeling methods
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier

#import classification modeling reporting
from sklearn.metrics import classification_report



def split(df):
    '''
    This function splits data into the train, validate, and test set at portions: 56%, 24%, 20%, stratify on is_default 
    '''
    
    # This function splits data into the train, validate, and test set at portions: 56%, 24%, 20%, stratify on is_default
    train_validate, test = train_test_split(df, test_size=.2, random_state=123, stratify=df.is_default)
    train, validate = train_test_split(train_validate, test_size=.3, random_state=123, stratify=train_validate.is_default)

    return train, validate, test


def feature_engineering(train, validate, test):
    '''
    This function created column is_naics_defaulter that labels the top 3 naics with most defaults with 1. 
    It also labels the states with the largerst percentage of defaults as 1.
    '''

    # make column where naics top defaulter are 1
    train['is_naics_defaulter'] = np.where(train.naics.isin([722110, 722211, 811111]), 1, 0)
    validate['is_naics_defaulter'] = np.where(validate.naics.isin([722110, 722211, 811111]), 1, 0)
    test['is_naics_defaulter'] = np.where(test.naics.isin([722110, 722211, 811111]), 1, 0)


    # select states for new columns
    state_cols = ['FL', 'GA', 'NV', 'AZ', 'MI', 'CA', 'DC', 'IL', 'NJ', 'TN', 'SC', 'CO', 'UT', 'NC', 'NY', 'VA', 'TX', 'AL', 'IN','MD', 'LA', 'KY', 'OR', 'OH']

    # create new column that lables the states with highest percentage of defaulted loans
    train['is_state_defaulter'] = np.where(train.state.isin(state_cols), 1, 0)
    validate['is_state_defaulter'] = np.where(validate.state.isin(state_cols), 1, 0)
    test['is_state_defaulter'] = np.where(test.state.isin(state_cols), 1, 0)

    return train, validate, test


def X_y(train, validate, test):
    '''
    This function selects columns to create X_y versions of train, validate, and test
    '''
    
    # Select columns to scale for feature selection and modeling
    cols = [
    'term',
     'emp_num',
     'jobs_created',
     'jobs_retained',
     'appv_loan_amount',
     'sba_appv_amount',
     'is_new',
     'sba_percent',
     'monthly_debt',
     'jobs_count',
     'is_default',
     'is_naics_defaulter',
     'is_state_defaulter'
    ]

    # establish target column
    target = 'is_default'

    # create X & y version of train, validate, test with y the target and X are the features. 
    X_train = train[cols].drop(columns=[target])
    y_train = train[[target]]

    X_validate = validate[cols].drop(columns=[target])
    y_validate = validate[[target]]

    X_test = test[cols].drop(columns=[target])
    y_test = test[[target]]

    return X_train, y_train, X_validate, y_validate, X_test, y_test



def scale(X_train, X_validate, X_test):
    '''
    This function scaled X_train, X_validate, and X_test with MinMax Scaler
    '''
    # Create the scale container
    scaler = MinMaxScaler()

    # Fit the scaler to the features
    scaler.fit(X_train)

    # create scaled X versions 
    X_train_scaled = scaler.transform(X_train)
    X_validate_scaled = scaler.transform(X_validate)
    X_test_scaled = scaler.transform(X_test)

    # Convert numpy array to pandas dataframe for feature Engineering
    X_train_scaled = pd.DataFrame(X_train_scaled, index=X_train.index, columns=X_train.columns.to_list())
    X_validate_scaled = pd.DataFrame(X_validate_scaled, index=X_validate.index, columns=X_validate.columns.to_list())
    X_test_scaled = pd.DataFrame(X_test_scaled, index=X_test.index, columns=X_test.columns.to_list())

    return X_train_scaled, X_validate_scaled, X_test_scaled


def select_k_best(X_train_scaled, y_train):
    '''
    This function takes X_train_scaled and y_train and identifies 3 best features using select k best
    '''
    # Use f_regression stats test each column to find best 3 features
    f_selector = SelectKBest(f_regression, k=3)

    # find tthe best correlations with y
    f_selector.fit(X_train_scaled, y_train)

    # Creaet boolean mask of the selected columns. 
    feature_mask = f_selector.get_support()

    # get list of top K features. 
    f_feature = X_train_scaled.iloc[:,feature_mask].columns.tolist()

    return f_feature


def rfe(X_train_scaled, y_train):
    '''
    This function takes X_train_scaled and y_train to identify best 3 features using linear gression
    '''
    # create the ML algorithm container
    lm = LinearRegression()

    # create the rfe container with the the number of features I want. 
    rfe = RFE(lm, n_features_to_select=3)

    # fit RFE to the data
    rfe.fit(X_train_scaled,y_train)  

    # get the mask of the selected columns
    feature_mask = rfe.support_

    # get list of the column names. 
    rfe_feature = X_train_scaled.iloc[:,feature_mask].columns.tolist()

    return rfe_feature



def dt_train(X_train_scaled, y_train):
    '''
    This function creates the Decision Tree container, fits it to X_train data, makes a prediction,
    builds a classifcation report
    '''

    # Create Decision Tree Container
    clf = DecisionTreeClassifier(max_depth=3, random_state=123)

    # Fit Data to Container
    clf = clf.fit(X_train_scaled, y_train)

    # Create Prediction
    y_pred_clf = clf.predict(X_train_scaled)
    
    # Create Classification Report for Model 1 on train
    print(classification_report(y_train, y_pred_clf))
    
    return clf


def dt_validate(X_validate_scaled, y_validate, clf):
    '''
    This function makes a prediction on X_validate_scaled and build a classification report
    '''
    
    y_pred_clf = clf.predict(X_validate_scaled)
    
    # Create classification report model 1 on validate
    print(classification_report(y_validate, y_pred_clf))
    
    return


def rf_train(X_train_scaled, y_train):
    '''
    This function makes the Random Forest Container, fits it to X_train_scaled, makes a prediction, 
    then it builds a classification report
    '''
    
    # Create Random Forest Classifier Container
    rf = RandomForestClassifier(max_depth=3, random_state=123)

    # Fit Train to Container
    rf = rf.fit(X_train_scaled, y_train)

    # Create Prediction 
    y_pred_rf = rf.predict(X_train_scaled)
    
    # Create Classification Report for Model 2 on train
    print(classification_report(y_train, y_pred_rf))
    
    return rf


def rf_validate(X_validate_scaled, y_validate, rf):
    '''
    Uses randome fortest containter to predict on X_validate
    '''
    
    # Create Prediction Series
    y_pred_rf = rf.predict(X_validate_scaled)
    
    # Create Classification Report for Model 2 on validate
    print(classification_report(y_validate, y_pred_rf))
    
    return


def knn_train(X_train_scaled, y_train):
    '''
    This function creates the knn container, fits it to X_train, makes a prediction,
    and builds a classification report
    '''

    # Create Decision Tree Classifier Algorithym Container
    knn = KNeighborsClassifier(n_neighbors=3, weights='uniform')

    # Fit Train Data to Container to make the model
    knn = knn.fit(X_train_scaled, y_train)

    # Create Prediction Series
    y_pred_knn = knn.predict(X_train_scaled)
    
    # Create Classification Report for Model 3 train
    print(classification_report(y_train, y_pred_knn))
    
    return knn


def knn_validate(X_validate_scaled, y_validate, knn):
    '''
    This function make a prediction on X_validate_scaled and builds a classification report
    '''
        
    # Create Prediction Series
    y_pred_knn = knn.predict(X_validate_scaled)
    
    # Create Classification Report for Model 3 on validate
    print(classification_report(y_validate, y_pred_knn))

    return 


def knn_test(X_test_scaled, y_test, knn):
    '''
    This function makes a knn prediction on test data and builds a report
    '''

    # Create Prediction Series
    y_pred_knn = knn.predict(X_test_scaled)
    
    # Create classification report for model 3 on test data
    print(classification_report(y_test, y_pred_knn))

    return






    
    
import matplotlib.pyplot as plt
import streamlit as st

class sensor:

	def __init__(self, v_harvest, v_bot, v_nobot, v_no, v_typical, v_high, p_storm):
		self.v_harvest = v_harvest
		self.v_bot = v_bot
		self.v_nobot = v_nobot
		self.v_no = v_no
		self.v_typical = v_typical
		self.v_high = v_high
		self.p_storm = p_storm

	def computation(self, sensitivity, specificity, p_botrytis, p_no, p_typical, p_high):
		"""
			Take the models performances, and the probability to compute the brought value
		"""
		recom = "" # This is the recommendation string

		e_s = self.v_bot * p_botrytis + self.v_nobot * (1 - p_botrytis)
		e_ns = self.v_no * p_no + self.v_typical * p_typical + self.v_high * p_high

		p_dns = specificity * (1 - self.p_storm) + (1 - specificity) * self.p_storm

		p_ns = specificity * (1 - self.p_storm)

		p_ns_dns = p_ns / p_dns

		p_ds = sensitivity * self.p_storm + (1 - sensitivity) * (1 - self.p_storm)

		p_s = sensitivity * self.p_storm

		p_s_ds = p_s / p_ds

		e_dns_noharvest = e_s * (1 - p_ns_dns) + e_ns * p_ns_dns

		e_dns = max(e_dns_noharvest, self.v_harvest)

		if e_dns_noharvest > self.v_harvest:
			recom += "If the detector predicts that there is no storm, wait and don't harvest now.\n"
		else:
			recom += "If the detector predicts that there is no storm, harvest now.\n"


		e_ds_noharvest = e_s * p_s_ds + e_ns * (1 - p_s_ds)

		e_ds = max(e_ds_noharvest, self.v_harvest)

		if e_ds_noharvest > self.v_harvest:
			recom += "If the detector predicts that there is storm, wait and don't harvest now.\n"
		else:
			recom += "If the detector predicts that there is storm, harvest now.\n"

		e_buy = p_dns * e_dns + p_ds * e_ds

		return (max(self.v_harvest, e_buy) - self.v_harvest, recom)

def find_indifference(s):
	# This function is intended to find the indifference point
	# Assume that the specificity and the sensitivity are the same
	performances = []
	values = []
	spec = 0
	while spec < 1:
		performances.append(spec)
		diff = s.computation(spec, spec, 0.1, 0.6, 0.3, 0.1)[0]
		values.append(diff)

		if abs(diff <= 0.001):
			print("The difference point is: %.2f" % (spec))
		# Update the spec by 0.01
		spec += 0.01
	# Plot the distribution
	plt.plot(performances, values)


def main():
	s = sensor(960000, 3300000, 420000, 960000, 1410000, 1500000, 0.5)
	ui_render(s)
	# find_indifference(s)

def ui_render(s):
	st.title("Storm Prediction Help Decision Making")
	st.header("You can change the following likelihoods to see the recommendations:")
	p_botrytis = st.slider("Prob of Botrytis: ", 0.0, 1.0, 0.1, 0.1)
	p_no = st.slider("Prob of No Sugar :", 0.0, 1.0, 0.6, 0.1)
	p_typical = st.slider("Prob of Typical Sugar: ", 0.0, 1.0, 0.3, 0.1)
	p_high = st.slider("Prob of High Sugar: ", 0.0, 1.0, 0.1, 0.1)

	if abs(p_no + p_typical + p_high - 1) > 0.01:
		# Invalid input, change the value
		st.write("You must make sure that the total prob of the last three to be 1")
	else:
		com_res = s.computation(0.375, 1, p_botrytis, p_no, p_typical, p_high)
		e_detector = com_res[0]
		recom = com_res[1]
		st.write("E-value of the Decision: ", e_detector)

		st.write("The alternative is: ", recom)

if __name__ == '__main__':
	main()







